import { useQueries } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { MetricsResponse } from "../types/company";

export function useMetricsBatch(tickers: string[]) {
  return useQueries({
    queries: tickers.map((ticker) => ({
      queryKey: ["metrics", ticker],
      queryFn: async () => {
        const { data } = await api.get<MetricsResponse>(
          `/api/company/${ticker}/metrics`
        );
        return data;
      },
      enabled: !!ticker,
      staleTime: 24 * 60 * 60 * 1000,
    })),
  });
}
