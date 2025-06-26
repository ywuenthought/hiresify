// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import type { TabProps } from '@mui/material';
import { Tab } from '@mui/material';

interface AuthTabProps extends TabProps {
  onTop: boolean;
}

function AuthTab({ onTop, ...props }: AuthTabProps) {
  return (
    <Tab
      {...props}
      sx={{
        backgroundColor: onTop ? '#d3d3d3' : '#ffffff',
        border: 1,
        borderBottom: onTop ? 1 : 0,
        borderRadius: '8px 8px 0 0',
        fontWeight: onTop ? 'bold' : 'normal',
        minWidth: 120,
        mr: 1,
      }}
    />
  );
}

export default AuthTab;
