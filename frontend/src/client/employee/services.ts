import { UUID } from "crypto"
import type { CancelablePromise } from "../core/CancelablePromise"
import { OpenAPI } from "../core/OpenAPI"
import { request as __request } from "../core/request"

import type {
  EmployeeCreate,
  EmployeePublic,
  EmployeesPublic,
  EmployeeUpdate,
  NewInvite
} from "../employee/models"
import type { Message } from "../user/models"

export type TDataReadEmployees = {
  business_id: string
  limit?: number
  skip?: number
}
export type TDataCreateEmployeeUserByInvite = {
  requestBody: NewInvite
}
export type TDataInvite ={
  email: string
  business_id: string
}
export type TDataCreateEmployee = {
  requestBody: EmployeeCreate
}
export type TDataReadEmployeeWithBiz = {
  id: string
  business_id: string
}
export type TDataUpdateEmployee = {
  id: string
  requestBody: EmployeeUpdate
}
export type TDataDeleteEmployee = {
  id: string
}
export type TDataUpdateEmployeeAvatar = {
  avatarFile: File
}


export class EmployeesService {
  /**
   * Read Employee Me
   * Get current employee.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static readEmployeeMe(): CancelablePromise<EmployeePublic> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/employee/",
    })
  }
  
  /**
   * Read Employees
   * Retrieve items.
   * @returns EmployeesPublic Successful Response
   * @throws ApiError
   */

  public static readEmployees(
    data: TDataReadEmployees,
  ): CancelablePromise<EmployeesPublic> {
    const { limit = 100, skip = 0, business_id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/employee/business",
      query: {
        skip,
        limit,
        business_id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  
  /**
   * Create Employee first time right after business creation
   * NOT USABLE first employee registers with Business service create_business_with_industry_employee
   * Create new Employee.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static createEmployeeFirst(
    data: TDataCreateEmployee,
  ): CancelablePromise<EmployeePublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/employee/first",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Read Employee
   * Get item by ID and Buziness ID.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static readEmployeeWithBiz(data: TDataReadEmployeeWithBiz): CancelablePromise<EmployeePublic> {
    const { id, business_id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/employee/{id}&{business_id}",
      path: {
        id,
        business_id
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Invite New Employee and User using invitation letter
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */

  public static inviteEmployee(data: TDataInvite): CancelablePromise<Message> {
    // /invite_employee/{email}/{business_id}
    const { email, business_id } = data

    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/employee/invite_employee/",
      query: {
        email,
        business_id
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Create Employee and User using invitation letter
   * Create new Employee.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static RegisterNewUserEmployeeByInvite(
    data: TDataCreateEmployeeUserByInvite,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/employee/register-by-invitation/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Employee
   * Update an item.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static updateEmployee(
    data: TDataUpdateEmployee,
  ): CancelablePromise<EmployeePublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/employee/{id}",
      path: {
        id,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Post avatar file for Employee
   * Post an avatar file for Employee.
   * @returns EmployeePublic Successful Response
   * @throws ApiError
   */
  public static updateEmployeeAvatar(
    data: TDataUpdateEmployeeAvatar,
  ): CancelablePromise<EmployeePublic> {
    const { avatarFile } = data
    console.log(avatarFile)
    const formData = new FormData()
    formData.append('file', avatarFile)

    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/employee/update_avatar/",
      body: formData,
      mediaType: "multipart/form-data",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete Employee
   * Delete an item.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteEmployee(data: TDataDeleteEmployee): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/employee/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
