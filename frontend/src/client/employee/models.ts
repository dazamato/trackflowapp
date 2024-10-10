export type EmployeeCreateBusiness = {
  name: string
  description?: string | null
  role?: string | null
}

export type EmployeeCreate = {
  name: string
  description?: string | null
  role?: string | null
  business_id: string
}

export type EmployeePublic = {
  id: string
  name: string
  description?: string | null
  role?: string | null
  business_id: string
  is_active?: boolean
  user_id: string
  // business: Array<BusinessPublic>
  created_at: Date
  updated_at: Date
}

export type EmployeeUpdate = {
  name?: string | null
  description?: string | null
  role?: string | null
  business_id?: string | null
}

export type EmployeesPublic = {
  data: Array<EmployeePublic>
  count: number
}
