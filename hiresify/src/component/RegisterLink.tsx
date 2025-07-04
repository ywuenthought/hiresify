// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { LinkBaseProps } from '@mui/material';
import { Link } from '@mui/material';

import { userUrls } from '@/const';

export default function RegisterLink(props: LinkBaseProps) {
  return (
    <Link
      fontWeight="bold"
      href={userUrls.register}
      rel="noopener noreferrer"
      underline="hover"
      target="_blank"
      variant="subtitle1"
      {...props}
    >
      Register
    </Link>
  );
}
