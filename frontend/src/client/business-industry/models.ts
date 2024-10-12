export type BusinessIndustryCreate = {
  title: string
  description?: string | null
  market_value?: number | null
  image?: string | null
}

export type BusinessIndustryPublic = {
  title: string
  description?: string | null
  market_value?: number | null
  image?: string | null
  id: string
  created_at: Date
  updated_at: Date
}

export type BusinessIndustryUpdate = {
  title?: string | null
  description?: string | null
  market_value?: number | null
  image?: string | null
}

export type BusinessIndustriesPublic = {
  data: Array<BusinessIndustryPublic>
  count: number
}