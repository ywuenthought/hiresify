// Copyright (c) 2025 Yifeng Wu
// This file is part of incredible-me and is licensed under the MIT License.
// See the LICENSE file for more details.

import { Delete, InsertDriveFile, Movie, Photo } from '@mui/icons-material';
import {
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';

type FileProfileProps = {
  fileName: string;
  fileType?: 'image' | 'video';
  removeFile: () => void;
};

export default function FileProfile(props: FileProfileProps) {
  const { fileName, fileType } = props;
  const { removeFile } = props;

  let mediaIcon;

  switch (fileType) {
    case 'image':
      mediaIcon = <Photo />;
      break;
    case 'video':
      mediaIcon = <Movie />;
      break;
    default:
      mediaIcon = <InsertDriveFile />;
      break;
  }

  return (
    <ListItem
      secondaryAction={
        <IconButton onClick={removeFile}>
          <Delete />
        </IconButton>
      }
    >
      <ListItemIcon>{mediaIcon}</ListItemIcon>
      <ListItemText primary={fileName} />
    </ListItem>
  );
}
