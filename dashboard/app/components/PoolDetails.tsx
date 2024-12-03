"use client"
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Button, Typography, Grid, CircularProgress } from "@mui/material";

// Register necessary components from Chart.js
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface HistoricalData {
  apy: number;
  apyBase: number;
  tvlUsd: number;
}

interface PoolDetailsProps {
  poolId: string;
  onBack: () => void;
}

const PoolDetails: React.FC<PoolDetailsProps> = ({ poolId, onBack }) => {
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); // Error state

  // Function to clean the data (replace NaN with null)
  const cleanData = (data: any[]) => {
    return data.map((item) => ({
      ...item,
      apy: isNaN(item.apy) ? null : item.apy,
      apyBase: isNaN(item.apyBase) ? null : item.apyBase,
      tvlUsd: isNaN(item.tvlUsd) ? null : item.tvlUsd,
    }));
  };

  useEffect(() => {
    const fetchHistoricalData = async () => {
      setLoading(true); // Set loading to true
      setError(null); // Reset error state
      try {
        const response = await fetch(`http://localhost:5001/historical_apy/${poolId}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const text = await response.text();
        const sanitizedText = text.replace(/NaN/g, 'null'); // Replace NaN with null as text
        const data = JSON.parse(sanitizedText);
        const cleanedData = cleanData(data); // Clean NaN values here
        setHistoricalData(cleanedData);
      } catch (error) {
        console.error("Error fetching historical data: ", error);
        setError(error.message); // Set error message
      } finally {
        setLoading(false); // Set loading to false
      }
    };

    fetchHistoricalData();
  }, [poolId]);

  if (loading) return <CircularProgress />;
  if (error) return <Typography align="center" color="error">{error}</Typography>;

  const chartData = {
    labels: historicalData.map((_, index) => `Point ${index + 1}`),
    datasets: [
      {
        label: "APY",
        data: historicalData.map((item) => item.apy),
        borderColor: "rgba(75,192,192,1)",
        fill: false,
      },
      {
        label: "APY Base",
        data: historicalData.map((item) => item.apyBase),
        borderColor: "rgba(153,102,255,1)",
        fill: false,
      },
      {
        label: "TVL (USD)",
        data: historicalData.map((item) => item.tvlUsd),
        borderColor: "rgba(255,159,64,1)",
        fill: false,
      },
    ],
  };

  return (
    <div className="container">
      <Typography variant="h4" align="center">Pool Details - {poolId}</Typography>
      <Grid container justifyContent="center" style={{ margin: '20px 0' }}>
        <Button variant="outlined" onClick={onBack}>Back</Button>
      </Grid>
      <Line data={chartData} />
    </div>
  );
};

export default PoolDetails;