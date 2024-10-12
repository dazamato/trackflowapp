import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"

import { AxiosError } from "axios"
import {
//   type Body_login_login_access_token as AccessToken,
  type ApiError,
  type EmployeePublic,
  EmployeesService,
  BusinessesService,
  type BusinessCreate,

} from "../client"
import useCustomToast from "./useCustomToast"

const isEmployee = () => {
  return localStorage.getItem("employee_id") !== null
}

const useEmployee = () => {
    const [error, setError] = useState<string | null>(null)
    const navigate = useNavigate()
    const showToast = useCustomToast()
    const queryClient = useQueryClient()
    const { data: employee, isLoading } = useQuery<EmployeePublic | null, Error> ({
      queryKey: ["currentEmployee"],
      queryFn: EmployeesService.readEmployeeMe,
      enabled: isEmployee(),
    })
    const setEmployee = (data: EmployeePublic) => {
        localStorage.setItem("access_token", data.business_id)
    }
    const unsetEmployee = () => {
        localStorage.removeItem("access_token")
        queryClient.invalidateQueries({ queryKey: ["currentEmployee"] })
    }
    const registerEmployee = async (data: BusinessCreate) => { 
        console.log("data", data)
        const employee_reg = await BusinessesService.createBusinessEmployee({ requestBody: data })
        localStorage.setItem("employee_id", employee_reg.id)
    }

    const businessRegisterMutation = useMutation({
        mutationFn: (data: BusinessCreate) => registerEmployee(data),
        onSuccess: () => {
          navigate({ to: "/" })
          showToast(
            "Business created.",
            "Your Business has been registered successfully.",
            "success",
          )
        },
        onError: (err: ApiError) => {
          let errDetail = (err.body as any)?.detail
    
          if (err instanceof AxiosError) {
            errDetail = err.message
          }
    
          showToast("Something went wrong.", errDetail, "error")
        },
        onSettled: () => {
          queryClient.invalidateQueries({ queryKey: ["employee"] })
        },
      })

    return {
        businessRegisterMutation,
        employee,
        unsetEmployee,
        setEmployee,
        isLoading,
        error,
        resetError: () => setError(null),
      }
    }
    
export { isEmployee }
export default useEmployee
    