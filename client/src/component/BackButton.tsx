// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Home } from '@mui/icons-material';
import type { ButtonProps } from '@mui/material';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

import { routes } from '@/routes';

export default function BackButton(props: ButtonProps) {
  const navigate = useNavigate();

  return (
    <Button
      color="primary"
      fullWidth
      size="large"
      startIcon={<Home />}
      variant="contained"
      onClick={() => navigate(routes.home.root)}
      {...props}
    >
      Back to Home
    </Button>
  );
}
