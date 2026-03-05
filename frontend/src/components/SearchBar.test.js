import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from './SearchBar';

test('renders search input and button', () => {
    render(<SearchBar onSearch={() => { }} />);
    const inputElement = screen.getByPlaceholderText(/Search tasks.../i);
    expect(inputElement).toBeInTheDocument();

    const buttonElement = screen.getByRole('button');
    expect(buttonElement).toBeInTheDocument();
});

test('calls onSearch when submitted', () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const inputElement = screen.getByPlaceholderText(/Search tasks.../i);
    fireEvent.change(inputElement, { target: { value: 'bug' } });

    const buttonElement = screen.getByRole('button');
    fireEvent.click(buttonElement);

    expect(mockOnSearch).toHaveBeenCalledWith('bug');
});
