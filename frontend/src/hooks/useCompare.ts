import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { CompareResponse } from "../types/compare";

export function useCompare(tickers: string[]) {
  const key = tickers.slice().sort().join(",");
  return useQuery({
    queryKey: ["compare", key],
    queryFn: async () => {
      const { data } = await api.post<CompareResponse>("/api/compare/", {
        tickers,
      });
      return data;
    },
    enabled: tickers.length >= 2,
    staleTime: 15 * 60 * 1000,
  });
}
