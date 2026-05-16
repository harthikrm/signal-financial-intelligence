import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { IndicatorsResponse } from "../types/company";

export function useIndicators(ticker: string | null) {
  return useQuery({
    queryKey: ["indicators", ticker],
    queryFn: async () => {
      const { data } = await api.get<IndicatorsResponse>(
        `/api/company/${ticker}/indicators`
      );
      return data;
    },
    staleTime: 15 * 60 * 1000,
    enabled: !!ticker,
  });
}
