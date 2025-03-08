import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import App from './App';

// very basic test more directed towards figuring out github actions 

test('Test 1: renders Select a Stock', () => {
  render(<App />);
  expect(screen.getByText(/Select a Stock/i)).toBeInTheDocument();
});

test('Test 2: selecting a stock updates the text', () => { //sample for selecting apple
  render(<App />);
  fireEvent.change(screen.getByRole('combobox'), { target: { value: 'AAPL' } });
  expect(screen.getByText(/You selected: AAPL/i)).toBeInTheDocument();
});
