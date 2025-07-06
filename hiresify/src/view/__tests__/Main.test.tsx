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

import { routes } from '@/const';
import { getUuid4, setManyItems } from '@/util';

import Main from '../Main';

describe('Main view', () => {
  beforeEach(() => {
    sessionStorage.clear();
    mockNavigate.mockClear();
  });

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<Main />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to home when there is no refresh token', async () => {
    // When
    render(<Main />);

    // Then
    expect(mockNavigate).toHaveBeenCalledWith(routes.home.root);
  });

  it('does not navigate when there is a refresh token', async () => {
    // Given
    const refreshToken = getUuid4();
    setManyItems({ refreshToken });

    // When
    render(<Main />);

    // Then
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
