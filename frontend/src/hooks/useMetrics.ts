import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { MetricsResponse } from "../types/company";

export function useMetrics(ticker: string | null) {
  return useQuery({
    queryKey: ["metrics", ticker],
    queryFn: async () => {
      const { data } = await api.get<MetricsResponse>(
        `/api/company/${ticker}/metrics`
      );
      return data;
    },
    staleTime: 24 * 60 * 60 * 1000,
    enabled: !!ticker,
  });
}
