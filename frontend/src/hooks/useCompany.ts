import { useQuery } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { Company } from "../types/company";

export function useCompany(ticker: string | null) {
  return useQuery({
    queryKey: ["company", ticker],
    queryFn: async () => {
      const { data } = await api.get<Company>(`/api/company/${ticker}`);
      return data;
    },
    staleTime: 24 * 60 * 60 * 1000,
    enabled: !!ticker,
  });
}
