import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Stack,
  CircularProgress,
  Alert,
  Pagination,
  useMediaQuery
} from '@mui/material';
import { 
  Search, 
  FilterList, 
  Clear,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Timeline,
  Assessment
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useTheme } from '@mui/material/styles';
import RecommendationCard from './RecommendationCard';
import RecommendationDetailsDialog from './RecommendationDetailsDialog';
import AddToPortfolioDialog from '../portfolio/AddToPortfolioDialog';
import { useAuth } from '../../context/AuthContext';
import { useSavedRecommendations } from '../../hooks/useSavedRecommendations';

/**
 * Recommendations list component
 * 
 * @param {Array} recommendations - List of recommendations
 * @param {boolean} loading - Whether recommendations are loading
 * @param {string} error - Error message if any
 * @param {Function} onRefresh - Function to refresh recommendations
 * @param {Object} filters - Current filter values
 * @param {Function} onFilterChange - Function to handle filter changes
 */
const RecommendationsList = ({ 
  recommendations = [], 
  loading = false, 
  error = null,
  onRefresh,
  filters = {},
  onFilterChange
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { isAuthenticated } = useAuth();
  const { savedRecommendations, saveRecommendation, removeRecommendation } = useSavedRecommendations();
  
  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);
  const [showPortfolioDialog, setShowPortfolioDialog] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  
  // Filter options
  const actionOptions = [
    { value: 'all', label: t('filters.all') },
    { value: 'buy', label: t('recommendation.action.buy') },
    { value: 'sell', label: t('recommendation.action.sell') },
    { value: 'hold', label: t('recommendation.action.hold') }
  ];
  
  const timeFrameOptions = [
    { value: 'all', label: t('filters.all') },
    { value: 'short', label: t('recommendation.timeFrame.short') },
    { value: 'medium', label: t('recommendation.timeFrame.medium') },
    { value: 'long', label: t('recommendation.timeFrame.long') }
  ];
  
  const typeOptions = [
    { value: 'all', label: t('filters.all') },
    { value: 'technical', label: t('recommendation.type.technical') },
    { value: 'fundamental', label: t('recommendation.type.fundamental') },
    { value: 'mixed', label: t('recommendation.type.mixed') }
  ];
  
  // Filter recommendations
  const filteredRecommendations = recommendations.filter(rec => {
    // Search term filter
    const matchesSearch = searchTerm === '' || 
      (rec.stock.symbol && rec.stock.symbol.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (rec.stock.name && rec.stock.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (rec.stock.sector && rec.stock.sector.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Action filter
    const matchesAction = filters.action === 'all' || filters.action === rec.action;
    
    // Time frame filter
    const matchesTimeFrame = filters.timeFrame === 'all' || filters.timeFrame === rec.time_frame;
    
    // Type filter
    const matchesType = filters.type === 'all' || filters.type === rec.type;
    
    // Confidence filter
    const matchesConfidence = !filters.minConfidence || rec.confidence >= filters.minConfidence;
    
    // Sector filter
    const matchesSector = !filters.sector || filters.sector === 'all' || 
      (rec.stock.sector && rec.stock.sector === filters.sector);
    
    return matchesSearch && matchesAction && matchesTimeFrame && 
           matchesType && matchesConfidence && matchesSector;
  });
  
  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredRecommendations.slice(indexOfFirstItem, indexOfLastItem);
  const pageCount = Math.ceil(filteredRecommendations.length / itemsPerPage);
  
  // Handle page change
  const handlePageChange = (event, value) => {
    setCurrentPage(value);
    window.scrollTo(0, 0);
  };
  
  // Handle search
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1);
  };
  
  // Clear search
  const handleClearSearch = () => {
    setSearchTerm('');
    setCurrentPage(1);
  };
  
  // Handle filter change
  const handleFilterChange = (name, value) => {
    onFilterChange({ ...filters, [name]: value });
    setCurrentPage(1);
  };
  
  // Handle view details
  const handleViewDetails = (recommendation) => {
    setSelectedRecommendation(recommendation);
    setShowDetailsDialog(true);
  };
  
  // Handle add to portfolio
  const handleAddToPortfolio = (recommendation) => {
    setSelectedRecommendation(recommendation);
    setShowPortfolioDialog(true);
  };
  
  // Handle save/unsave recommendation
  const handleSaveRecommendation = (recommendation) => {
    const isSaved = savedRecommendations.some(
      saved => saved.stock.symbol === recommendation.stock.symbol
    );
    
    if (isSaved) {
      removeRecommendation(recommendation);
    } else {
      saveRecommendation(recommendation);
    }
  };
  
  // Check if a recommendation is saved
  const isRecommendationSaved = (recommendation) => {
    return savedRecommendations.some(
      saved => saved.stock.symbol === recommendation.stock.symbol
    );
  };
  
  // Reset filters
  const handleResetFilters = () => {
    onFilterChange({
      action: 'all',
      timeFrame: 'all',
      type: 'all',
      minConfidence: 0,
      sector: 'all'
    });
    setSearchTerm('');
    setCurrentPage(1);
  };
  
  // Get active filter count
  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.action && filters.action !== 'all') count++;
    if (filters.timeFrame && filters.timeFrame !== 'all') count++;
    if (filters.type && filters.type !== 'all') count++;
    if (filters.minConfidence && filters.minConfidence > 0) count++;
    if (filters.sector && filters.sector !== 'all') count++;
    if (searchTerm) count++;
    return count;
  };
  
  const activeFilterCount = getActiveFilterCount();
  
  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h5" component="h1" gutterBottom>
          {t('recommendations.title')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('recommendations.description')}
        </Typography>
      </Box>
      
      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center">
            <FilterList sx={{ mr: 1 }} />
            <Typography variant="subtitle1">
              {t('filters.title')}
            </Typography>
          </Box>
          
          {activeFilterCount > 0 && (
            <Chip 
              label={t('filters.reset')}
              size="small"
              onDelete={handleResetFilters}
              deleteIcon={<Clear />}
            />
          )}
        </Box>
        
        <Grid container spacing={2}>
          {/* Search */}
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              fullWidth
              variant="outlined"
              size="small"
              label={t('filters.search')}
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={handleClearSearch}
                      edge="end"
                    >
                      <Clear />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          
          {/* Action Filter */}
          <Grid item xs={6} sm={3} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="action-filter-label">{t('filters.action')}</InputLabel>
              <Select
                labelId="action-filter-label"
                value={filters.action || 'all'}
                label={t('filters.action')}
                onChange={(e) => handleFilterChange('action', e.target.value)}
              >
                {actionOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Time Frame Filter */}
          <Grid item xs={6} sm={3} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="time-frame-filter-label">{t('filters.timeFrame')}</InputLabel>
              <Select
                labelId="time-frame-filter-label"
                value={filters.timeFrame || 'all'}
                label={t('filters.timeFrame')}
                onChange={(e) => handleFilterChange('timeFrame', e.target.value)}
              >
                {timeFrameOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Type Filter */}
          <Grid item xs={6} sm={3} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="type-filter-label">{t('filters.type')}</InputLabel>
              <Select
                labelId="type-filter-label"
                value={filters.type || 'all'}
                label={t('filters.type')}
                onChange={(e) => handleFilterChange('type', e.target.value)}
              >
                {typeOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Confidence Filter */}
          <Grid item xs={6} sm={3} md={2}>
            <TextField
              fullWidth
              type="number"
              variant="outlined"
              size="small"
              label={t('filters.minConfidence')}
              value={filters.minConfidence || ''}
              onChange={(e) => handleFilterChange('minConfidence', e.target.value)}
              InputProps={{
                endAdornment: <InputAdornment position="end">%</InputAdornment>,
                inputProps: { min: 0, max: 100 }
              }}
            />
          </Grid>
        </Grid>
        
        {/* Active Filters */}
        {activeFilterCount > 0 && (
          <Box mt={2}>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {filters.action && filters.action !== 'all' && (
                <Chip 
                  size="small"
                  label={`${t('filters.action')}: ${actionOptions.find(o => o.value === filters.action)?.label}`}
                  onDelete={() => handleFilterChange('action', 'all')}
                  icon={
                    filters.action === 'buy' ? <TrendingUp fontSize="small" /> :
                    filters.action === 'sell' ? <TrendingDown fontSize="small" /> :
                    <TrendingFlat fontSize="small" />
                  }
                />
              )}
              
              {filters.timeFrame && filters.timeFrame !== 'all' && (
                <Chip 
                  size="small"
                  label={`${t('filters.timeFrame')}: ${timeFrameOptions.find(o => o.value === filters.timeFrame)?.label}`}
                  onDelete={() => handleFilterChange('timeFrame', 'all')}
                  icon={<Timeline fontSize="small" />}
                />
              )}
              
              {filters.type && filters.type !== 'all' && (
                <Chip 
                  size="small"
                  label={`${t('filters.type')}: ${typeOptions.find(o => o.value === filters.type)?.label}`}
                  onDelete={() => handleFilterChange('type', 'all')}
                  icon={<Assessment fontSize="small" />}
                />
              )}
              
              {filters.minConfidence > 0 && (
                <Chip 
                  size="small"
                  label={`${t('filters.minConfidence')}: ${filters.minConfidence}%`}
                  onDelete={() => handleFilterChange('minConfidence', 0)}
                />
              )}
              
              {filters.sector && filters.sector !== 'all' && (
                <Chip 
                  size="small"
                  label={`${t('filters.sector')}: ${filters.sector}`}
                  onDelete={() => handleFilterChange('sector', 'all')}
                />
              )}
              
              {searchTerm && (
                <Chip 
                  size="small"
                  label={`${t('filters.search')}: ${searchTerm}`}
                  onDelete={handleClearSearch}
                  icon={<Search fontSize="small" />}
                />
              )}
            </Stack>
          </Box>
        )}
      </Paper>
      
      {/* Results */}
      <Box mb={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="subtitle1">
            {t('recommendations.results', { count: filteredRecommendations.length })}
          </Typography>
        </Box>
        
        <Divider sx={{ mb: 3 }} />
        
        {/* Loading State */}
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" py={4}>
            <CircularProgress />
          </Box>
        )}
        
        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        {/* Empty State */}
        {!loading && !error && filteredRecommendations.length === 0 && (
          <Box 
            display="flex" 
            flexDirection="column" 
            justifyContent="center" 
            alignItems="center" 
            py={4}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {t('recommendations.noResults')}
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              {activeFilterCount > 0 
                ? t('recommendations.tryAdjustingFilters')
                : t('recommendations.noRecommendationsAvailable')}
            </Typography>
          </Box>
        )}
        
        {/* Recommendations List */}
        {!loading && !error && currentItems.length > 0 && (
          <Box>
            {currentItems.map((recommendation) => (
              <RecommendationCard
                key={`${recommendation.stock.symbol}-${recommendation.type}`}
                recommendation={recommendation}
                onSave={handleSaveRecommendation}
                onViewDetails={handleViewDetails}
                onAddToPortfolio={handleAddToPortfolio}
                isSaved={isAuthenticated && isRecommendationSaved(recommendation)}
              />
            ))}
          </Box>
        )}
        
        {/* Pagination */}
        {!loading && !error && pageCount > 1 && (
          <Box display="flex" justifyContent="center" mt={4}>
            <Pagination
              count={pageCount}
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
              size={isMobile ? "small" : "medium"}
              showFirstButton
              showLastButton
            />
          </Box>
        )}
      </Box>
      
      {/* Recommendation Details Dialog */}
      <RecommendationDetailsDialog
        open={showDetailsDialog}
        onClose={() => setShowDetailsDialog(false)}
        recommendation={selectedRecommendation}
        onAddToPortfolio={handleAddToPortfolio}
        isSaved={isAuthenticated && selectedRecommendation && isRecommendationSaved(selectedRecommendation)}
        onSave={handleSaveRecommendation}
      />
      
      {/* Add to Portfolio Dialog */}
      <AddToPortfolioDialog
        open={showPortfolioDialog}
        onClose={() => setShowPortfolioDialog(false)}
        stock={selectedRecommendation?.stock}
        recommendedPrice={selectedRecommendation?.price}
        targetPrice={selectedRecommendation?.target_price}
        stopLoss={selectedRecommendation?.stop_loss}
      />
    </Box>
  );
};

export default RecommendationsList;