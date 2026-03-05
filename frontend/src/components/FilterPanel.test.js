import { render, screen, fireEvent } from '@testing-library/react';
import FilterPanel from './FilterPanel';

test('renders all filter buttons', () => {
    render(<FilterPanel currentFilter="all" onFilterChange={() => { }} />);
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Done')).toBeInTheDocument();
    expect(screen.getByText('Today')).toBeInTheDocument();
});

test('calls onFilterChange when a button is clicked', () => {
    const mockOnFilterChange = jest.fn();
    render(<FilterPanel currentFilter="all" onFilterChange={mockOnFilterChange} />);

    fireEvent.click(screen.getByText('Active'));
    expect(mockOnFilterChange).toHaveBeenCalledWith('active');
});
