import React from 'react';
import { Box } from '@mui/material';
import PropTypes from 'prop-types';

/**
 * TabPanel component for Material UI Tabs
 * 
 * @param {Object} props - Component props
 * @param {ReactNode} props.children - Tab content
 * @param {number} props.value - Current tab index
 * @param {number} props.index - This tab's index
 * @param {Object} props.sx - Additional styles
 */
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

export default TabPanel;