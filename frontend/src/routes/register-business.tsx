import {
  Button,
  Container,
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Image,
  Input,
  Link,
  Text,
  Select,
} from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm, FormProvider, useFormContext } from "react-hook-form"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"

import Logo from "/assets/images/trackflow-logo.svg"
import type { BusinessCreate, EmployeeCreateBusiness, BusinessIndustryPublic } from "../client"
import { BusinessIndustriesService } from "../client"
import useEmloyee, { isEmployee } from "../hooks/useEmployee"
import { emailPattern } from "../utils"

export const Route = createFileRoute("/register-business")({
  component: BusinessRegistration,
  beforeLoad: async () => {
    if (isEmployee()) {
      throw redirect({
        to: "/",
      })
    }
  },
})
function getIndustry() {
  return {
    queryFn: () =>
      BusinessIndustriesService.readAllBusinessIndustries(),
    queryKey: ["industries"],
  }
}


interface EmployeeCreateBusinessForm extends BusinessCreate {
  employee_in: EmployeeCreateBusiness
}

function BusinessIndustryDropdown() {
  const { register } = useFormContext()
  const queryClient = useQueryClient()
  const {
    data: industries,
    // isPending,
    // isPlaceholderData,
  } = useQuery({
    ...getIndustry(),
  })

  useEffect(() => {
      queryClient.prefetchQuery(getIndustry())
  }, [queryClient])

  return (
    <FormControl id="business_industry_id" isInvalid>
      <FormLabel htmlFor="business_industry_id" srOnly>
        Business Industry
      </FormLabel>
      <Select
        id="business_industry_id"
        placeholder="Business Industry"
        {...register("business_industry_id", { required: "Role is required" })}
        // onSelect={setIndustry} 
      >
        {industries?.data.map((industry: BusinessIndustryPublic) => (
          <option key={industry.id} value={industry.id}>
            {industry.title}
          </option>
        )
        )
        }
      </Select>
    </FormControl>
  )
}

function BusinessRegistration() {
  const { businessRegisterMutation } = useEmloyee()

  const formMethods = useForm<EmployeeCreateBusinessForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      organizational_type: "",
      national_id: "",
      national_id_type: "",
      country: "",
      city: "",
      address: "",
      phone: "",
      email: "",
      website: "",
      bank_account: "",
      logo: "",
      is_active: true,
      business_industry_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      employee_in: {
        name: "",
        description: "",
        role: "",
      },
    },
  })
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = formMethods

  const onSubmit: SubmitHandler<EmployeeCreateBusinessForm> = (data) => {
    businessRegisterMutation.mutate(data)
  }

  return (
    <>
    <FormProvider {...formMethods}>
      <Flex flexDir={{ base: "column", md: "row" }} justify="center" h="100vh">
        <Container
          as="form"
          onSubmit={handleSubmit(onSubmit)}
          h="100vh"
          maxW="sm"
          alignItems="stretch"
          justifyContent="center"
          gap={4}
          centerContent
        >
          <Image
            src={Logo}
            alt="TrackFlow logo"
            height="auto"
            maxW="2xs"
            alignSelf="center"
            mb={4}
          />
          <FormControl id="name" isInvalid={!!errors.name}>
            <FormLabel htmlFor="name" srOnly>
              Official Business Name
            </FormLabel>
            <Input
              id="name"
              minLength={3}
              {...register("name", { required: "Official Business Name is required" })}
              placeholder="Official Business Name"
              type="text"
            />
            {errors.name && (
              <FormErrorMessage>{errors.name.message}</FormErrorMessage>
            )}
          </FormControl>

          <FormControl id="employee_in.name" isInvalid={!!errors.employee_in?.name}>
            <FormLabel htmlFor="employee_in.name" srOnly>
              Your role name in Company
            </FormLabel>
            <Input
              id="employee_in.name"
              minLength={3}
              {...register("employee_in.name", { required: "Your Your role name in Company" })}
              placeholder="Your role name in Company"
              type="text"
            />
            {errors.employee_in?.name && (
              <FormErrorMessage>{errors.employee_in?.name?.message}</FormErrorMessage>
            )}
          </FormControl>
          <FormControl id="email" isInvalid={!!errors.email}>
            <FormLabel htmlFor="email" srOnly>
              Your Business Email
            </FormLabel>
            <Input
              id="email"
              {...register("email", {
                required: "Business Email is required",
                pattern: emailPattern,
              })}
              placeholder="Business Email"
              type="email"
            />
            {errors.email && (
              <FormErrorMessage>{errors.email.message}</FormErrorMessage>
            )}
          </FormControl>
          <BusinessIndustryDropdown/>
          <Button variant="primary" type="submit" isLoading={isSubmitting}>
            Register
          </Button>
          <Text>
            If you dont want register your business?{" "}
            <Link as={RouterLink} to="/" color="blue.500">
              Go to main page
            </Link>
          </Text>
        </Container>
      </Flex>
      </FormProvider>
    </>
  )
}

export default BusinessRegistration  