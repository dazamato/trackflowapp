import type { CancelablePromise } from "../core/CancelablePromise"
import { OpenAPI } from "../core/OpenAPI"
import { request as __request } from "../core/request"

import type {
  BusinessCreate,
  BusinessPublic,
  BusinessesPublic,
  BusinessUpdate,
} from "../business/models"
import type { Message } from "../user/models"

export type TDataReadBusinesses = {
  limit?: number
  skip?: number
}
export type TDataCreateBusiness = {
  requestBody: BusinessCreate
}
export type TDataReadBusiness = {
  id: string
}
export type TDataUpdateBusiness = {
  id: string
  requestBody: BusinessUpdate
}
export type TDataDeleteBusiness = {
  id: string
}

export class BusinessesService {
  /**
   * Read All Businesses 
   * Retrieve businesss.
   * @returns BusinessesPublic Successful Response
   * @throws ApiError
   */
  public static readAllBusinesses(
    data: TDataReadBusinesses = {},
  ): CancelablePromise<BusinessesPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/business/all/",
      query: {
        skip,
        limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create Business
   * Create new business.
   * @returns BusinessPublic Successful Response
   * @throws ApiError
   */
  public static createBusinessEmployee(
    data: TDataCreateBusiness,
  ): CancelablePromise<BusinessPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/business/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read Business
   * Get business by ID.
   * @returns BusinessPublic Successful Response
   * @throws ApiError
   */
  public static readBusinessByID(data: TDataReadBusiness): CancelablePromise<BusinessPublic> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/business/by_id/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  /**
   * Read My Business (read_my_business)
   * Get business of User.
   * @returns BusinessPublic Successful Response
   * @throws ApiError
   */
  public static readMyBusiness(): CancelablePromise<BusinessPublic> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/business/",
      errors: {
        422: `Validation Error`,
      },
    })
  }
  
  /**
   * Update Business
   * Update an business.
   * @returns BusinessPublic Successful Response
   * @throws ApiError
   */
  public static updateBusiness(
    data: TDataUpdateBusiness,
  ): CancelablePromise<BusinessPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/business/{id}",
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
   * Delete Business
   * Delete an business.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteBusiness(data: TDataDeleteBusiness): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/business/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
