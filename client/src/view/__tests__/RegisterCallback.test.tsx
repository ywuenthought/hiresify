// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );

  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import { render } from '@testing-library/react';

import RegisterCallback from '../RegisterCallback';

describe('RegisterCallback view', () => {
  it('renders something', () => {
    // When
    const { baseElement: root } = render(<RegisterCallback />);

    // Then
    expect(root).toBeTruthy();
  });

  it('congratulates when the registration succeeded', () => {
    // When
    const { getByTestId } = render(<RegisterCallback />);

    // Then
    const success = getByTestId('success');
    expect(success).toHaveTextContent('Congratulations!');
  });
});
