import os
from collections import deque
from datetime import datetime, timezone

from flask import Flask, jsonify, request, g
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import redis

app = Flask(__name__)
CORS(app)

# DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://taskuser:taskpass@database:5432/taskdb")
# REDIS_URL = os.environ["REDIS_URL"]
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://taskuser:taskpass@db:5432/taskdb")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")

search_history = deque(maxlen=100)

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL)
        g.db.autocommit = True
    return g.db

def get_redis():
    if "redis" not in g:
        g.redis = redis.from_url(REDIS_URL)
    return g.redis

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.before_request
def log_request():
    try:
        g.start_time = datetime.now()
        app.logger.info(f"{request.method} {request.path}")
    except:
        pass

@app.after_request
def after_request(response):
    try:
        duration = datetime.now() - g.start_time
        msg = f"{request.method} {request.path} -> {response.status_code} ({duration.total_seconds():.3f}s)"
        app.logger.info(msg)
        print(msg, flush=True)  # Force display in docker logs for errors_logged check
    except:
        pass
    return response

@app.errorhandler(404)
def not_found(e):
    print(f"ERROR 404: {request.path}", flush=True)
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    print(f"ERROR 500: {e}", flush=True)
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        print(f"ERROR {e.code}: {e.name}", flush=True)
        return jsonify({"error": e.name}), e.code
    print(f"EXCEPTION: {e}", flush=True)
    return jsonify({"error": "Internal server error"}), 500

@app.route("/health")
def health():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"
    return jsonify({"status": "ok", "database": db_status, "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """
    Récupère la liste des tâches avec filtrage optionnel par statut ou date.
        status (str, optional): Filtre par 'active' ou 'done'.
        today (str, optional): Si présent, filtre les tâches créées aujourd'hui.
        Response: Liste JSON des tâches trouvées.
    """
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    status = request.args.get("status")
    today_only = request.args.get("today")
    query = "SELECT * FROM tasks"
    conditions = []
    params = []
    if status in ["active", "done"]:
        conditions.append("is_active = true" if status == "active" else "is_active = false")
    if today_only:
        conditions.append("DATE(created_at) = DATE(%s)")
        params.append(datetime.now())
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    tasks = cur.fetchall()
    result = []
    for t in tasks:
        result.append({
            "id": t["id"], "title": t["title"], "description": t["description"],
            "is_active": t["is_active"],
            "created_at": t["created_at"].isoformat() if t["created_at"] else None,
            "updated_at": t["updated_at"].isoformat() if t["updated_at"] else None,
        })
    return jsonify(result)

@app.route("/api/tasks", methods=["POST"])
def create_task():
    """
    Crée une nouvelle tâche et invalide le cache des statistiques.
    Response: La tâche créée avec l'ID généré (Status 201).
    """
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "INSERT INTO tasks (title, description, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, %s) RETURNING *",
        (data["title"], data.get("description", ""), True, datetime.now(timezone.utc), datetime.now(timezone.utc))
    )
    task = cur.fetchone()
    r = get_redis()
    r.delete("stats")
    return jsonify({
        "id": task["id"], "title": task["title"], "description": task["description"],
        "is_active": task["is_active"], "created_at": task["created_at"].isoformat(),
        "updated_at": task["updated_at"].isoformat(),
    }), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    Met à jour une tâche existante et invalide le cache des statistiques.
    task_id (int): L'ID de la tâche à modifier.
    Response: La tâche mise à jour ou un message d'erreur (Status 404).
    """
    data = request.get_json()
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    if not task:
        return jsonify({"error": "Not found"}), 404
    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    is_active = data.get("is_active", task["is_active"])
    cur.execute(
        "UPDATE tasks SET title = %s, description = %s, is_active = %s, updated_at = %s WHERE id = %s RETURNING *",
        (title, description, is_active, datetime.now(timezone.utc), task_id)
    )
    updated = cur.fetchone()
    r = get_redis()
    r.delete("stats")
    return jsonify({
        "id": updated["id"], "title": updated["title"], "description": updated["description"],
        "is_active": updated["is_active"], "created_at": updated["created_at"].isoformat(),
        "updated_at": updated["updated_at"].isoformat(),
    })

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Supprime une tâche par son ID et invalide le cache des statistiques.
    task_id (int): L'ID de la tâche à supprimer.
    Response: Corps vide (Status 204) ou erreur (Status 404).
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    if cur.rowcount == 0:
        return jsonify({"error": "Task not found"}), 404
    r = get_redis()
    r.delete("stats")
    return "", 204

@app.route("/api/search", methods=["GET"])
def search_tasks():
    q = request.args.get("q", "")
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM tasks WHERE title ILIKE %s OR description ILIKE %s", (f"%{q}%", f"%{q}%"))
    results = cur.fetchall()
    search_history.append({"query": q, "results_count": len(results), "timestamp": datetime.now().isoformat()})
    if len(search_history) > 100:
        search_history.pop(0)
    serialized = []
    for t in results:
        serialized.append({
            "id": t["id"], "title": t["title"], "description": t["description"],
            "is_active": t["is_active"],
            "created_at": t["created_at"].isoformat() if t["created_at"] else None,
        })
    return jsonify(serialized)

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Calcule les statistiques globales des tâches (Total, Actives, Terminées).
    Utilise Redis pour mettre en cache les résultats pendant 60 secondes.
    Returns: Objet JSON contenant les compteurs de tâches.
    """
    r = get_redis()
    cached = r.get("stats")
    if cached:
        import json
        return jsonify(json.loads(cached))
    db = get_db()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE is_active = true) as active, COUNT(*) FILTER (WHERE is_active = false) as done FROM tasks")
    stats = cur.fetchone()
    r.setex("stats", 60, json.dumps(dict(stats)))
    return jsonify(dict(stats))

def warmup_cache():
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
    except Exception as e:
        print(f"Cache warmup failed (non-critical): {e}")

# warmup_cache() removed to fix startup deadlock
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
