import type { CancelablePromise } from "../core/CancelablePromise"
import { OpenAPI } from "../core/OpenAPI"
import { request as __request } from "../core/request"

import type {
  BusinessIndustryCreate,
  BusinessIndustryPublic,
  BusinessIndustriesPublic,
  BusinessIndustryUpdate,
} from "../business-industry/models"
import type { Message } from "../user/models"

export type TDataReadBusinessIndustries = {
  limit?: number
  skip?: number
}
export type TDataCreateBusinessIndustry = {
  requestBody: BusinessIndustryCreate
}
export type TDataReadBusinessIndustry = {
  id: string
}
export type TDataUpdateBusinessIndustry = {
  id: string
  requestBody: BusinessIndustryUpdate
}
export type TDataDeleteBusinessIndustry = {
  id: string
}

export class BusinessIndustriesService {
  /**
   * Read All BusinessIndustries 
   * Retrieve businesss.
   * @returns BusinessIndustriesPublic Successful Response
   * @throws ApiError
   */
  
  public static readAllBusinessIndustries(
    data: TDataReadBusinessIndustries = {},
  ): CancelablePromise<BusinessIndustriesPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/business_industry/",
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
   * Create BusinessIndustry
   * Create new business.
   * @returns BusinessIndustryPublic Successful Response
   * @throws ApiError
   */
  public static createBusinessIndustry(
    data: TDataCreateBusinessIndustry,
  ): CancelablePromise<BusinessIndustryPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/business_industry/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read BusinessIndustry
   * Get business by ID.
   * @returns BusinessIndustryPublic Successful Response
   * @throws ApiError
   */
  public static readBusinessIndustryByID(data: TDataReadBusinessIndustry): CancelablePromise<BusinessIndustryPublic> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/business_industry/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
  
  /**
   * Update BusinessIndustry
   * Update an business.
   * @returns BusinessIndustryPublic Successful Response
   * @throws ApiError
   */
  public static updateBusinessIndustry(
    data: TDataUpdateBusinessIndustry,
  ): CancelablePromise<BusinessIndustryPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/business_industry/{id}",
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
   * Delete BusinessIndustry
   * Delete an business.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteBusinessIndustry(data: TDataDeleteBusinessIndustry): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/business_industry/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
