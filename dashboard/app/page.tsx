"use client"
import React, { useEffect, useState } from "react";
import PoolList from "./components/PoolList";
import PoolDetails from "./components/PoolDetails";

interface Pool {
  pool: string;
  project: string;
  symbol: string;
  tvlUsd: number;
  apy: number;
}

export default function Home() {
  const [pools, setPools] = useState<Pool[]>([]);
  const [selectedPool, setSelectedPool] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:5001/pools')
      .then((res) => res.text()) // Read response as plain text
      .then((text) => {
        const sanitizedText = text.replace(/NaN/g, 'null'); // Replace NaN with null
        return JSON.parse(sanitizedText);
      })
      .then((data) => setPools(data))
      .catch((err) => console.error('Fetch error:', err));
  }, []);
  

  return (
    <div>
      {selectedPool ? (
        <PoolDetails
          poolId={selectedPool}
          onBack={() => setSelectedPool(null)}
        />
      ) : (
        <PoolList pools={pools} onSelectPool={setSelectedPool} />
      )}
    </div>
  );
}
