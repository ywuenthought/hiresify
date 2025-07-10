// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Logout } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import { routes, tokenUrls } from '@/const';

export default function LogoutButton(props: ButtonProps) {
  const navigate = useNavigate();

  const handleClick = async () => {
    // Send a request to revoke the refresh token.
    await fetch(tokenUrls.revoke, { method: 'POST' });

    // Navigate to home after a logout.
    navigate(routes.home.root);
  };

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Logout />}
      variant="text"
      onClick={handleClick}
      {...props}
    >
      Log Out
    </Button>
  );
}
