import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Divider, 
  Grid, 
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  IconButton
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  TrendingFlat,
  Timeline,
  ShowChart,
  Assessment,
  Info,
  Bookmark,
  BookmarkBorder,
  ArrowUpward,
  ArrowDownward,
  Remove
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { formatCurrency, formatPercentage } from '../../utils/formatters';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../../context/AuthContext';

/**
 * Stock recommendation card component
 * 
 * @param {Object} recommendation - The recommendation object
 * @param {Function} onSave - Function to call when saving a recommendation
 * @param {Function} onViewDetails - Function to call when viewing recommendation details
 * @param {Function} onAddToPortfolio - Function to call when adding to portfolio
 * @param {boolean} isSaved - Whether the recommendation is saved
 */
const RecommendationCard = ({ 
  recommendation, 
  onSave, 
  onViewDetails, 
  onAddToPortfolio,
  isSaved = false
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const { isAuthenticated } = useAuth();
  
  if (!recommendation) return null;
  
  const { 
    stock, 
    action, 
    confidence, 
    target_price, 
    stop_loss, 
    time_frame,
    price,
    technical_signals = [],
    fundamental_signals = []
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
  
  return (
    <Card 
      elevation={3} 
      sx={{ 
        mb: 2, 
        borderLeft: `5px solid ${getActionColor(action)}`,
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6
        }
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Box>
            <Typography variant="h6" component="div">
              {stock.symbol}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {stock.name}
            </Typography>
          </Box>
          <Box>
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
        </Box>
        
        {/* Price and Confidence */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" component="div">
            {formatCurrency(price)}
          </Typography>
          <Tooltip title={t('recommendation.confidenceTooltip')}>
            <Box display="flex" alignItems="center">
              <Typography variant="body2" color="text.secondary" mr={1}>
                {t('recommendation.confidence')}:
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {confidence}%
              </Typography>
            </Box>
          </Tooltip>
        </Box>
        
        <Divider sx={{ my: 1.5 }} />
        
        {/* Target and Stop Loss */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {t('recommendation.targetPrice')}
              </Typography>
              <Box display="flex" alignItems="center">
                <Typography variant="body1" fontWeight="bold">
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
                <Typography variant="body1" fontWeight="bold">
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
        
        {/* Time Frame and Sector */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Chip 
            size="small"
            icon={<Timeline fontSize="small" />}
            label={getTimeFrameText(time_frame)}
            sx={{ bgcolor: theme.palette.grey[200] }}
          />
          {stock.sector && (
            <Chip 
              size="small"
              label={stock.sector}
              sx={{ bgcolor: theme.palette.grey[200] }}
            />
          )}
        </Box>
        
        <Divider sx={{ my: 1.5 }} />
        
        {/* Signals */}
        <Box mb={2}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {t('recommendation.keySignals')}
          </Typography>
          <List dense disablePadding>
            {technical_signals.slice(0, 2).map((signal, index) => (
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
            {fundamental_signals.slice(0, 2).map((signal, index) => (
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
        </Box>
        
        {/* Risk/Reward Indicator */}
        {action !== 'hold' && (
          <Box display="flex" alignItems="center" mb={2}>
            <Typography variant="body2" color="text.secondary" mr={1}>
              {t('recommendation.riskReward')}:
            </Typography>
            <Chip 
              size="small"
              label={isRiskRewardFavorable ? 
                t('recommendation.favorable') : 
                t('recommendation.unfavorable')}
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
        )}
        
        {/* Actions */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Button 
            variant="outlined" 
            size="small"
            startIcon={<Info />}
            onClick={() => onViewDetails(recommendation)}
          >
            {t('recommendation.viewDetails')}
          </Button>
          
          <Box>
            {isAuthenticated && (
              <Tooltip title={isSaved ? t('recommendation.removeFromSaved') : t('recommendation.saveRecommendation')}>
                <IconButton 
                  size="small" 
                  onClick={() => onSave(recommendation)}
                  color={isSaved ? 'primary' : 'default'}
                >
                  {isSaved ? <Bookmark /> : <BookmarkBorder />}
                </IconButton>
              </Tooltip>
            )}
            
            {isAuthenticated && action === 'buy' && (
              <Button 
                variant="contained" 
                size="small"
                color="primary"
                sx={{ ml: 1 }}
                onClick={() => onAddToPortfolio(recommendation)}
              >
                {t('recommendation.addToPortfolio')}
              </Button>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;