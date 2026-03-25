import React from 'react';
import { useDispatch } from 'react-redux';
import { Snackbar, Alert, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { removeNotification } from '../../store/slices/uiSlice';

const Notifications = ({ notifications }) => {
  const dispatch = useDispatch();

  const handleClose = (id) => {
    dispatch(removeNotification(id));
  };

  return (
    <>
      {notifications.map((notification) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={notification.duration || 6000}
          onClose={() => handleClose(notification.id)}
          anchorOrigin={{
            vertical: notification.vertical || 'bottom',
            horizontal: notification.horizontal || 'left',
          }}
          sx={{ mb: notifications.indexOf(notification) * 8 }}
        >
          <Alert
            severity={notification.type || 'info'}
            variant="filled"
            action={
              <IconButton
                size="small"
                color="inherit"
                onClick={() => handleClose(notification.id)}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            }
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  );
};

export default Notifications;