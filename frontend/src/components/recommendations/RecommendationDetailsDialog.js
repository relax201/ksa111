import React from 'react';
import { 
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Chip,
  Divider,
  Grid,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Paper,
  useMediaQuery,
  Tab,
  Tabs
} from '@mui/material';
import { 
  Close,
  TrendingUp, 
  TrendingDown, 
  TrendingFlat,
  Timeline,
  ShowChart,
  Assessment,
  ArrowUpward,
  ArrowDownward,
  Remove,
  Bookmark,
  BookmarkBorder,
  BarChart,
  TableChart,
  Info,
  Warning
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useTheme } from '@mui/material/styles';
import { formatCurrency, formatPercentage, formatDate } from '../../utils/formatters';
import { useAuth } from '../../context/AuthContext';
import TabPanel from '../common/TabPanel';

/**
 * Recommendation details dialog component
 * 
 * @param {boolean} open - Whether the dialog is open
 * @param {Function} onClose - Function to close the dialog
 * @param {Object} recommendation - The recommendation object
 * @param {Function} onAddToPortfolio - Function to add to portfolio
 * @param {boolean} isSaved - Whether the recommendation is saved
 * @param {Function} onSave - Function to save/unsave the recommendation
 */
const RecommendationDetailsDialog = ({ 
  open, 
  onClose, 
  recommendation, 
  onAddToPortfolio,
  isSaved,
  onSave
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated } = useAuth();
  const [tabValue, setTabValue] = React.useState(0);
  
  if (!recommendation) return null;
  
  const { 
    stock, 
    action, 
    confidence, 
    target_price, 
    stop_loss, 
    time_frame,
    price,
    type,
    notes,
    technical_signals = [],
    fundamental_signals = [],
    analysis_date,
    expiry_date
  } = recommendation;
  
  // Determine action color
  const getActionColor = (action) => {
    switch(action) {
      case 'buy':
        return theme.palette.success.main;
      case 'sell':
        return theme.palette.error.main;
      default:
        return theme.palette.warning.main;
    }
  };
  
  // Determine action icon
  const getActionIcon = (action) => {
    switch(action) {
      case 'buy':
        return <TrendingUp />;
      case 'sell':
        return <TrendingDown />;
      default:
        return <TrendingFlat />;
    }
  };
  
  // Determine time frame text
  const getTimeFrameText = (timeFrame) => {
    switch(timeFrame) {
      case 'short':
        return t('recommendation.timeFrame.short');
      case 'medium':
        return t('recommendation.timeFrame.medium');
      case 'long':
        return t('recommendation.timeFrame.long');
      default:
        return t('recommendation.timeFrame.medium');
    }
  };
  
  // Calculate potential return
  const calculateReturn = () => {
    if (!price || !target_price) return 0;
    return ((target_price - price) / price) * 100;
  };
  
  // Calculate risk (distance to stop loss)
  const calculateRisk = () => {
    if (!price || !stop_loss) return 0;
    return ((price - stop_loss) / price) * 100;
  };
  
  const potentialReturn = calculateReturn();
  const risk = calculateRisk();
  
  // Determine if the risk/reward ratio is favorable
  const isRiskRewardFavorable = Math.abs(potentialReturn) > Math.abs(risk) * 2;
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullScreen={fullScreen}
      maxWidth="md"
      fullWidth
      scroll="paper"
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {t('recommendationDetails.title')}
          </Typography>
          <IconButton edge="end" onClick={onClose} aria-label="close">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <Divider />
      
      <DialogContent>
        {/* Header */}
        <Box mb={3}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={8}>
              <Box display="flex" alignItems="center">
                <Typography variant="h5" component="div" mr={2}>
                  {stock.symbol}
                </Typography>
                <Chip 
                  icon={getActionIcon(action)} 
                  label={t(`recommendation.action.${action}`)}
                  sx={{ 
                    bgcolor: getActionColor(action),
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                />
              </Box>
              <Typography variant="body1" color="text.secondary">
                {stock.name}
              </Typography>
              {stock.sector && (
                <Typography variant="body2" color="text.secondary">
                  {stock.sector}
                </Typography>
              )}
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Box display="flex" flexDirection="column" alignItems={fullScreen ? "flex-start" : "flex-end"}>
                <Typography variant="h4" component="div" gutterBottom>
                  {formatCurrency(price)}
                </Typography>
                <Box display="flex" alignItems="center">
                  <Typography variant="body2" color="text.secondary" mr={1}>
                    {t('recommendation.confidence')}:
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {confidence}%
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Box>
        
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="recommendation details tabs"
            variant={fullScreen ? "fullWidth" : "standard"}
          >
            <Tab 
              icon={<Info />} 
              label={t('recommendationDetails.tabs.summary')} 
              id="tab-0" 
              aria-controls="tabpanel-0" 
            />
            <Tab 
              icon={<ShowChart />} 
              label={t('recommendationDetails.tabs.technical')} 
              id="tab-1" 
              aria-controls="tabpanel-1" 
            />
            <Tab 
              icon={<Assessment />} 
              label={t('recommendationDetails.tabs.fundamental')} 
              id="tab-2" 
              aria-controls="tabpanel-2" 
            />
          </Tabs>
        </Box>
        
        {/* Summary Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {/* Target and Stop Loss */}
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('recommendationDetails.priceTargets')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {t('recommendation.targetPrice')}
                      </Typography>
                      <Box display="flex" alignItems="center">
                        <Typography variant="h6" fontWeight="bold">
                          {formatCurrency(target_price)}
                        </Typography>
                        <Tooltip title={t('recommendation.potentialReturn')}>
                          <Chip
                            size="small"
                            icon={potentialReturn > 0 ? <ArrowUpward fontSize="small" /> : 
                                  potentialReturn < 0 ? <ArrowDownward fontSize="small" /> : 
                                  <Remove fontSize="small" />}
                            label={formatPercentage(potentialReturn)}
                            sx={{ 
                              ml: 1,
                              bgcolor: potentialReturn > 0 ? theme.palette.success.light : 
                                      potentialReturn < 0 ? theme.palette.error.light : 
                                      theme.palette.grey[300],
                              color: potentialReturn > 0 ? theme.palette.success.contrastText : 
                                     potentialReturn < 0 ? theme.palette.error.contrastText : 
                                     theme.palette.grey[800],
                            }}
                          />
                        </Tooltip>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {t('recommendation.stopLoss')}
                      </Typography>
                      <Box display="flex" alignItems="center">
                        <Typography variant="h6" fontWeight="bold">
                          {formatCurrency(stop_loss)}
                        </Typography>
                        <Tooltip title={t('recommendation.risk')}>
                          <Chip
                            size="small"
                            icon={<ArrowDownward fontSize="small" />}
                            label={formatPercentage(risk)}
                            sx={{ 
                              ml: 1,
                              bgcolor: theme.palette.error.light,
                              color: theme.palette.error.contrastText
                            }}
                          />
                        </Tooltip>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
                
                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t('recommendation.riskReward')}:
                  </Typography>
                  <Chip 
                    size="small"
                    label={isRiskRewardFavorable ? 
                      t('recommendation.favorable') : 
                      t('recommendation.unfavorable')}
                    icon={isRiskRewardFavorable ? <ArrowUpward /> : <Warning />}
                    sx={{ 
                      bgcolor: isRiskRewardFavorable ? 
                        theme.palette.success.light : 
                        theme.palette.warning.light,
                      color: isRiskRewardFavorable ? 
                        theme.palette.success.contrastText : 
                        theme.palette.warning.contrastText
                    }}
                  />
                </Box>
              </Paper>
            </Grid>
            
            {/* Recommendation Details */}
            <Grid item xs={12} md={6}>
              <Paper elevation={1} sx={{ p: 2, height: '100%' }}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('recommendationDetails.details')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('recommendation.type.label')}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {t(`recommendation.type.${type}`)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('recommendation.timeFrame.label')}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {getTimeFrameText(time_frame)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('recommendationDetails.analysisDate')}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {formatDate(analysis_date)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      {t('recommendationDetails.expiryDate')}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {formatDate(expiry_date)}
                    </Typography>
                  </Grid>
                </Grid>
                
                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t('recommendationDetails.notes')}
                  </Typography>
                  <Typography variant="body2">
                    {notes || t('recommendationDetails.noNotes')}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            
            {/* Key Signals */}
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('recommendationDetails.keySignals')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={3}>
                  {/* Technical Signals */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      {t('recommendationDetails.technicalSignals')}
                    </Typography>
                    
                    {technical_signals.length > 0 ? (
                      <List dense>
                        {technical_signals.map((signal, index) => (
                          <ListItem key={`tech-${index}`} disablePadding sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <ShowChart fontSize="small" color="primary" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={signal}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        {t('recommendationDetails.noSignals')}
                      </Typography>
                    )}
                  </Grid>
                  
                  {/* Fundamental Signals */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      {t('recommendationDetails.fundamentalSignals')}
                    </Typography>
                    
                    {fundamental_signals.length > 0 ? (
                      <List dense>
                        {fundamental_signals.map((signal, index) => (
                          <ListItem key={`fund-${index}`} disablePadding sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <Assessment fontSize="small" color="secondary" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={signal}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        {t('recommendationDetails.noSignals')}
                      </Typography>
                    )}
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Technical Analysis Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            {/* Technical Analysis Summary */}
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('recommendationDetails.technicalAnalysis')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Typography variant="body2" paragraph>
                  {t('recommendationDetails.technicalAnalysisDescription')}
                </Typography>
                
                {/* Technical Signals */}
                <Typography variant="subtitle2" gutterBottom>
                  {t('recommendationDetails.technicalSignals')}
                </Typography>
                
                {technical_signals.length > 0 ? (
                  <List>
                    {technical_signals.map((signal, index) => (
                      <ListItem key={`tech-detail-${index}`} disablePadding sx={{ py: 0.5 }}>
                        <ListItemIcon>
                          <ShowChart color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={signal} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {t('recommendationDetails.noSignals')}
                  </Typography>
                )}
                
                {/* Placeholder for Technical Charts */}
                <Box 
                  mt={3} 
                  p={3} 
                  bgcolor={theme.palette.grey[100]} 
                  borderRadius={1}
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  justifyContent="center"
                >
                  <BarChart sx={{ fontSize: 48, color: theme.palette.grey[400], mb: 2 }} />
                  <Typography variant="body2" color="text.secondary" align="center">
                    {t('recommendationDetails.chartsPlaceholder')}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Fundamental Analysis Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            {/* Fundamental Analysis Summary */}
            <Grid item xs={12}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {t('recommendationDetails.fundamentalAnalysis')}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Typography variant="body2" paragraph>
                  {t('recommendationDetails.fundamentalAnalysisDescription')}
                </Typography>
                
                {/* Fundamental Signals */}
                <Typography variant="subtitle2" gutterBottom>
                  {t('recommendationDetails.fundamentalSignals')}
                </Typography>
                
                {fundamental_signals.length > 0 ? (
                  <List>
                    {fundamental_signals.map((signal, index) => (
                      <ListItem key={`fund-detail-${index}`} disablePadding sx={{ py: 0.5 }}>
                        <ListItemIcon>
                          <Assessment color="secondary" />
                        </ListItemIcon>
                        <ListItemText primary={signal} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {t('recommendationDetails.noSignals')}
                  </Typography>
                )}
                
                {/* Placeholder for Financial Tables */}
                <Box 
                  mt={3} 
                  p={3} 
                  bgcolor={theme.palette.grey[100]} 
                  borderRadius={1}
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  justifyContent="center"
                >
                  <TableChart sx={{ fontSize: 48, color: theme.palette.grey[400], mb: 2 }} />
                  <Typography variant="body2" color="text.secondary" align="center">
                    {t('recommendationDetails.tablesPlaceholder')}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </DialogContent>
      
      <Divider />
      
      <DialogActions sx={{ px: 3, py: 2 }}>
        {isAuthenticated && (
          <Button 
            startIcon={isSaved ? <Bookmark /> : <BookmarkBorder />}
            onClick={() => onSave(recommendation)}
            color={isSaved ? 'primary' : 'inherit'}
          >
            {isSaved ? t('recommendation.removeFromSaved') : t('recommendation.saveRecommendation')}
          </Button>
        )}
        
        <Box flexGrow={1} />
        
        <Button onClick={onClose} color="inherit">
          {t('common.close')}
        </Button>
        
        {isAuthenticated && action === 'buy' && (
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => {
              onAddToPortfolio(recommendation);
              onClose();
            }}
          >
            {t('recommendation.addToPortfolio')}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RecommendationDetailsDialog;