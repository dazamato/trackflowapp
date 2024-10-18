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
  type InviteRequest

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
        localStorage.setItem("employee_id", data.id)
        localStorage.setItem("business_id", data.business_id)
    }
    const unsetEmployee = () => {
        localStorage.removeItem("employee_id")
        localStorage.removeItem("business_id")
        queryClient.invalidateQueries({ queryKey: ["currentEmployee"] })
    }
    const registerEmployee = async (data: BusinessCreate) => { 
        const business = await BusinessesService.createBusinessEmployee({ requestBody: data })
        localStorage.setItem("business_id", business.id)
        const employee = await EmployeesService.readEmployeeMe()
        localStorage.setItem("employee_id", employee.id)
    }
    const employeeInvite = async (data: InviteRequest) => {
      await EmployeesService.inviteEmployee(data)
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
          queryClient.invalidateQueries({ queryKey: ["currentEmployee"] })
        },
      })
    
      const employeeInviteMutation = useMutation({
          mutationFn: (data: InviteRequest) => employeeInvite(data),
          onSuccess: () => {
            navigate({ to: "/" })
            showToast(
              "Invite sended.",
              "Your Invitation has been sended successfully.",
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
            queryClient.invalidateQueries({ queryKey: ["inviteRequest"] })
          },
      })

    return {
        businessRegisterMutation,
        employeeInviteMutation,
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
    