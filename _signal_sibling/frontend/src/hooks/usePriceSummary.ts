import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { PriceSummaryResponse } from "../types/company";

export function usePriceSummary(ticker: string | null) {
  return useQuery({
    queryKey: ["priceSummary", ticker],
    queryFn: async () => {
      const { data } = await api.get<PriceSummaryResponse>(
        `/api/company/${ticker}/price/summary`
      );
      return data;
    },
    staleTime: 15 * 60 * 1000,
    enabled: !!ticker,
  });
}
