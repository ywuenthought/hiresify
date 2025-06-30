// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { LinkBaseProps } from '@mui/material';
import { Link } from '@mui/material';

interface RegisterLinkProps extends LinkBaseProps {
  registerUrl: string;
}

export default function RegisterLink(props: RegisterLinkProps) {
  const { registerUrl, ...rest } = props;

  return (
    <Link
      fontWeight="bold"
      href={registerUrl}
      rel="noopener noreferrer"
      underline="hover"
      target="_blank"
      variant="subtitle1"
      {...rest}
    >
      Register
    </Link>
  );
}
