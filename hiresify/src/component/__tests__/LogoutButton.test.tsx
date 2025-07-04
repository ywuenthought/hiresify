// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { v4 as uuid4 } from 'uuid';

import { routes, tokenUrls } from '@/const';
import server from '@/testing/server';
import { setManyItems } from '@/util';

import LogoutButton from '../LogoutButton';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>(
      'react-router-dom'
    );

  return { ...actual, useNavigate: () => mockNavigate };
});

describe('LogoutButton UI component', () => {
  const calledEndpoints: string[] = [];

  beforeAll(() => {
    server.listen();

    server.events.on('request:start', ({ request }) =>
      calledEndpoints.push(request.url)
    );
  });

  beforeEach(() => {
    server.resetHandlers();

    calledEndpoints.length = 0;
    setManyItems({ refreshToken: uuid4() });
    mockNavigate.mockClear();
  });

  afterAll(() => {
    server.close();
  });

  it('renders something', () => {
    // When
    const { baseElement: root } = render(<LogoutButton />);

    // Then
    expect(root).toBeTruthy();
  });

  it('navigates to home after a click', async () => {
    // Given
    const { getByRole } = render(<LogoutButton />);

    // When
    const button = getByRole('button');
    await userEvent.click(button);

    // Then the endpoint was hit;
    expect(calledEndpoints).toEqual([tokenUrls.revoke]);
    // The session storage was reset;
    expect(sessionStorage).toHaveLength(0);
    // The navigation to home was made.
    expect(mockNavigate).toHaveBeenCalledWith(routes.home.root);
  });
});
