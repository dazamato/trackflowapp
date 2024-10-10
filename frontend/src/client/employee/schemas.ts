export const $EmployeeCreateBusiness = {
  properties: {
    name: {
      type: "string",
      isRequired: true,
      maxLength: 255,
      minLength: 1,
    },
    description: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
        },
        {
          type: "null",
        },
      ],
    },
    role: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 100,
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $EmployeeCreate = {
  properties: {
    name: {
      type: "string",
      isRequired: true,
      maxLength: 255,
      minLength: 1,
    },
    description: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
        },
        {
          type: "null",
        },
      ],
    },
    role: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 100,
        },
        {
          type: "null",
        },
      ],
    },
    business_id: {
      type: "string",
      isRequired: true,
      format: "uuid",
    },
  },
} as const

export const $EmployeePublic = {
  properties: {
    name: {
      type: "string",
      isRequired: true,
      maxLength: 255,
      minLength: 1,
    },
    description: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
        },
        {
          type: "null",
        },
      ],
    },
    role: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 100,
        },
        {
          type: "null",
        },
      ],
    },
    business_id: {
      type: "string",
      isRequired: true,
      format: "uuid",
    },
    id: {
      type: "string",
      isRequired: true,
      format: "uuid",
    },
    created_at: {
      type: "string",
      isRequired: true,
      format: "date-time",
    },
    updated_at: {
      type: "string",
      isRequired: true,
      format: "date-time",
    },
  },
} as const

export const $EmployeeUpdate = {
  properties: {
    name: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
        },
        {
          type: "null",
        },
      ],
    },
    description: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
        },
        {
          type: "null",
        },
      ],
    },
    role: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 100,
        },
        {
          type: "null",
        },
      ],
    },
    business_id: {
      type: "any-of",
      contains: [
        {
          type: "string",
          maxLength: 255,
          format: "uuid",
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $EmployeesPublic = {
  properties: {
    data: {
      type: "array",
      contains: {
        type: "EmployeePublic",
      },
      isRequired: true,
    },
    count: {
      type: "number",
      isRequired: true,
    },
  },
} as const
