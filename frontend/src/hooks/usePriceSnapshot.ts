import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { api } from "../lib/api";
import type { PriceSnapshotItem } from "../types/company";

export function usePriceSnapshot() {
  const query = useQuery({
    queryKey: ["priceSnapshot"],
    queryFn: async () => {
      const { data } = await api.get<PriceSnapshotItem[]>("/api/prices/snapshot");
      return data;
    },
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });

  const exchangeByTicker = useMemo(() => {
    const map: Record<string, string> = {};
    for (const row of query.data ?? []) {
      if (row.ticker && row.exchange) {
        map[row.ticker] = row.exchange;
      }
    }
    return map;
  }, [query.data]);

  return { ...query, exchangeByTicker };
}
