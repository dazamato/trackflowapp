import type {UserCreate} from '../user/models'
import type { BusinessPublic } from '../business/models'

export type EmployeeCreateBusiness = {
  name: string
  description?: string | null
  role?: string | null
  avatar?: string | null
}

export type EmployeeCreate = {
  name: string
  description?: string | null
  role?: string | null
  business_id: string
  avatar?: string | null
}

export type EmployeePublic = {
  id: string
  name: string
  description?: string | null
  role?: string | null
  avatar?: string | null
  business_id: string
  is_active?: boolean
  user_id: string
  business: Array<BusinessPublic>
  created_at: Date
  updated_at: Date
}

export type EmployeeUpdate = {
  name?: string | null
  description?: string | null
  role?: string | null
  avatar?: string | null
  business_id?: string | null
}

export type EmployeesPublic = {
  data: Array<EmployeePublic>
  count: number
}
export type NewInvite = {
  token: string
  new_user: Array<UserCreate>
  new_employee: Array<EmployeeCreateBusiness>
}
export type AvatarUploadInput = {
  avatarFile: FileList
}