"use client";

import React, { useEffect, useState } from "react";
import {
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Tooltip,
  TablePagination,
} from "@mui/material";
import { Skeleton } from "@mui/lab";

interface Pool {
  pool: string;
  project: string;
  symbol: string;
  tvlUsd: number;
  apy: number;
}

interface PoolListProps {
  onSelectPool: (poolId: string) => void;
}

const PoolList: React.FC<PoolListProps> = ({ onSelectPool }) => {
  const [pools, setPools] = useState<Pool[]>([]);
  const [filteredPools, setFilteredPools] = useState<Pool[]>([]);
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [filters, setFilters] = useState({ tvlMin: '', tvlMax: '', symbol: '', project: '' });
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [page, setPage] = useState(0); // Current page
  const [rowsPerPage, setRowsPerPage] = useState(50); // Rows per page

  // Fetch pool data once when the component mounts
  useEffect(() => {
    const fetchPools = async () => {
      setLoading(true); // Set loading to true
      setError(null); // Reset error state
      try {
        const response = await fetch('http://localhost:5001/pools');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const text = await response.text();
        const sanitizedText = text.replace(/NaN/g, 'null');
        const data = JSON.parse(sanitizedText);

        if (Array.isArray(data) && data.length > 0) {
          setPools(data);
          setFilteredPools(data); // Set filtered pools to all pools initially
        } else {
          throw new Error("No pool data available");
        }
      } catch (error) {
        console.error("Error fetching pool data:", error);
        setError(error.message); // Set error message
      } finally {
        setLoading(false); // Set loading to false
      }
    };

    fetchPools();
  }, []);

  // Sorting handler
  const sortedPools = React.useMemo(() => {
    if (!Array.isArray(filteredPools) || filteredPools.length < 1) {
      return filteredPools; // Return as is if not an array or empty
    }

    const sortablePools = [...filteredPools];
    if (sortConfig) {
      sortablePools.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortablePools;
  }, [filteredPools, sortConfig]);

  // Sorting function
  const handleSort = (key: string) => {
    const direction = sortConfig?.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc';
    setSortConfig({ key, direction });
  };

  // Filter handler for the Search button
  const handleSearch = () => {
    const { tvlMin, tvlMax, symbol, project } = filters;
    const newFilteredPools = pools.filter((pool) => {
      const tvlCondition = (tvlMin === '' || pool.tvlUsd >= Number(tvlMin)) &&
                           (tvlMax === '' || pool.tvlUsd <= Number(tvlMax));
      const symbolCondition = symbol === '' || pool.symbol.toLowerCase().includes(symbol.toLowerCase());
      const projectCondition = project === '' || pool.project.toLowerCase().includes(project.toLowerCase());
      return tvlCondition && symbolCondition && projectCondition;
    });
    setFilteredPools(newFilteredPools);
    setPage(0); // Reset to first page when filtering
  };

  // Filter input change handler
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({ ...prevFilters, [name]: value }));
  };

  // Handle page change
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset to first page when changing rows per page
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Typography align="center">Loading pool data...</Typography>
        <CircularProgress />
        <Skeleton variant="rect" width="100%" height={118} />
        <Skeleton variant="text" />
        <Skeleton variant="text" />
      </div>
    );
  }
  
  if (error) return <Typography align="center" color="error">{error}</Typography>;

  return (
    <div className="container">
      <Typography variant="h4" align="center">Pool List</Typography>

      {/* Filters */}
      <div className="filters">
        <TextField type="number" name="tvlMin" label="Min TVL" value={filters.tvlMin} onChange={handleFilterChange} margin="normal" />
        <TextField type="number" name="tvlMax" label="Max TVL" value={filters.tvlMax} onChange={handleFilterChange} margin="normal" />
        <TextField type="text" name="symbol" label="Search Symbol" value={filters.symbol} onChange={handleFilterChange} margin="normal" />
        <TextField type="text" name="project" label="Search Project" value={filters.project} onChange={handleFilterChange} margin="normal" />
        <Button variant="contained" onClick={handleSearch}>Search</Button>
      </div>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell onClick={() => handleSort('pool')} style={{ cursor: 'pointer' }}>Pool ID</TableCell>
              <TableCell onClick={() => handleSort('project')} style={{ cursor: 'pointer' }}>Project</TableCell>
              <TableCell onClick={() => handleSort('symbol')} style={{ cursor: 'pointer' }}>Symbol</TableCell>
              <TableCell onClick={() => handleSort('tvlUsd')} style={{ cursor: 'pointer' }}>TVL (USD)</TableCell>
              <TableCell onClick={() => handleSort('apy')} style={{ cursor: 'pointer' }}>APY</TableCell>
              <TableCell>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedPools.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((pool) => (
              <TableRow key={pool.pool} hover>
                <TableCell>{pool.pool}</TableCell>
                <TableCell>{pool.project}</TableCell>
                <TableCell>{pool.symbol}</TableCell>
                <TableCell>{pool.tvlUsd.toLocaleString()}</TableCell>
                <TableCell>{pool.apy}%</TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <Button variant="outlined" onClick={() => onSelectPool(pool.pool)}>View Details</Button>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        rowsPerPageOptions={[50, 75, 100]}
        component="div"
        count={filteredPools.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </div>
  );
};

export default PoolList;