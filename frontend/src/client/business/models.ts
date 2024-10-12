import type { EmployeeCreateBusiness } from '../employee/models'

export type BusinessCreate = {
  name: string
  organizational_type?: string | null
  national_id?: string | null
  national_id_type?: string | null
  country?: string | null
  city?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  website?: string | null
  bank_account?: string | null
  logo?: string | null
  is_active?: boolean | null
  business_industry_id: string | null
  employee_in: EmployeeCreateBusiness
}

export type BusinessPublic = {
  name: string
  organizational_type?: string | null
  national_id?: string | null
  national_id_type?: string | null
  country?: string | null
  city?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  website?: string | null
  bank_account?: string | null
  logo?: string | null
  is_active?: boolean | null
  id: string
  business_industry_id?: string | null
}

export type BusinessUpdate = {
  name?: string | null
  organizational_type?: string | null
  national_id?: string | null
  national_id_type?: string | null
  country?: string | null
  city?: string | null
  address?: string | null
  phone?: string | null
  email?: string | null
  website?: string | null
  bank_account?: string | null
  logo?: string | null
  is_active?: boolean | null
}

export type BusinessesPublic = {
  data: Array<BusinessPublic>
  count: number
}