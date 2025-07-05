// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );

  return { ...actual, useNavigate: () => mockNavigate };
});

import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { routes } from '@/const';

import BackButton from '../BackButton';

describe('BackButton UI component', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<BackButton />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to home after a click', async () => {
    // Given
    const { getByRole } = render(<BackButton />);

    // When
    const button = getByRole('button');
    await userEvent.click(button);

    // The navigation to home was made.
    expect(mockNavigate).toHaveBeenCalledWith(routes.home.root);
  });
});
