import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"

import { AxiosError } from "axios"
import {
//   type Body_login_login_access_token as AccessToken,
  type ApiError,
  type BusinessPublic,
  BusinessesService,
  type BusinessCreate,
  type BusinessUpdate,

} from "../client"
import useCustomToast from "./useCustomToast"

const isBusiness = () => {
    return localStorage.getItem("business_id") !== null
}
  
const useBusiness = () => {
    const [error, setError] = useState<string | null>(null)
    const navigate = useNavigate()
    const showToast = useCustomToast()
    const queryClient = useQueryClient()
    const { data: business, isLoading } = useQuery<BusinessPublic | null, Error> ({
    queryKey: ["currentBusiness"],
    queryFn: BusinessesService.readMyBusiness,
    enabled: isBusiness(),
    })
    const setBusiness = (data: BusinessPublic) => {
        localStorage.setItem("business_id", data.id)
    }
    const unsetBusiness = () => {
        localStorage.removeItem("business_id")
        queryClient.invalidateQueries({ queryKey: ["currentBusiness"] })
    }
    const updateBusiness = async (data: BusinessUpdate, ) => { 
        const id = localStorage.getItem("business_id")
        if (id!=null) {
            await BusinessesService.updateBusiness({ id: id, requestBody: data })
        }
    }
    const businessUpdateMutation = useMutation({
        mutationFn: (data: BusinessCreate) => updateBusiness(data),
        onSuccess: () => {
          navigate({ to: "/" })
          showToast(
            "Business updated.",
            "Your Business has been updated successfully.",
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
          queryClient.invalidateQueries({ queryKey: ["currentBusiness"] })
        },
    })

    return {
        businessUpdateMutation,
        business,
        unsetBusiness,
        setBusiness,
        isLoading,
        error,
        resetError: () => setError(null),
      }
    }
    
export { isBusiness }
export default useBusiness