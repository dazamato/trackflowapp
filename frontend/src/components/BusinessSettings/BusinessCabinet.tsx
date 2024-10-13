import {
    Box,
    Button,
    Container,
    Flex,
    FormControl,
    FormErrorMessage,
    FormLabel,
    Heading,
    Input,
    Text,
    useColorModeValue,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient } from "@tanstack/react-query"
  import { useState } from "react"
  import { type SubmitHandler, useForm } from "react-hook-form"
  
  import {
    type ApiError,
    type UserPublic,
    type BusinessPublic,
    type EmployeePublic,
    type UserUpdateMe,
    type EmployeeUpdate,
    UsersService,
    BusinessesService,
    EmployeesService,
  } from "../../client"
  import useAuth from "../../hooks/useAuth"
  import useEmployee from "../../hooks/useEmployee"
  import useCustomToast from "../../hooks/useCustomToast"
  import { emailPattern, handleError } from "../../utils"
  
  const BusinessCabinet = () => {
    const queryClient = useQueryClient()
    const color = useColorModeValue("inherit", "ui.light")
    const showToast = useCustomToast()
    const [editMode, setEditMode] = useState(false)
    const { employee: currentEmployee } = useEmployee()
    const {
      register,
      handleSubmit,
      reset,
      getValues,
      formState: { isSubmitting, errors, isDirty },
    } = useForm<EmployeePublic>({
      mode: "onBlur",
      criteriaMode: "all",
      defaultValues: {
        name: currentEmployee?.name,
        description: currentEmployee?.description,
        role: currentEmployee?.role,
      },
    })
  
    const toggleEditMode = () => {
      setEditMode(!editMode)
    }
  
    const mutation = useMutation({
      mutationFn: (data: EmployeeUpdate) =>
        EmployeesService.updateEmployee({ requestBody: data, id: currentEmployee!.id }),
      onSuccess: () => {
        showToast("Success!", "User updated successfully.", "success")
      },
      onError: (err: ApiError) => {
        handleError(err, showToast)
      },
      onSettled: () => {
        queryClient.invalidateQueries()
      },
    })
  
    const onSubmit: SubmitHandler<EmployeeUpdate> = async (data) => {
      mutation.mutate(data)
    }
  
    const onCancel = () => {
      reset()
      toggleEditMode()
    }
  
    return (
      <>
        <Container maxW="full">
          <Heading size="sm" py={4}>
            Company Information
          </Heading>
          <Box
            w={{ sm: "full", md: "50%" }}
            as="form"
            onSubmit={handleSubmit(onSubmit)}
          >
            <FormControl>
              <FormLabel color={color} htmlFor="name">
                Full name of employee
              </FormLabel>
              {editMode ? (
                <Input
                  id="name"
                  {...register("name", { maxLength: 30 })}
                  type="text"
                  size="md"
                  w="auto"
                />
              ) : (
                <Text
                  size="md"
                  py={2}
                  color={!currentEmployee?.name ? "ui.dim" : "inherit"}
                  isTruncated
                  maxWidth="250px"
                >
                  {currentEmployee?.name || "N/A"}
                </Text>
              )}
            </FormControl>
            <FormControl mt={4} isInvalid={!!errors.description}>
              <FormLabel color={color} htmlFor="description">
                Description of employee
              </FormLabel>
              {editMode ? (
                <Input
                  id="description"
                  {...register("description", { maxLength: 30 })}
                  type="text"
                  size="md"
                  w="auto"
                />
              ) : (
                <Text size="md" py={2} isTruncated maxWidth="250px">
                  {currentEmployee?.description || "N/A"}
                </Text>
              )}
              {errors.description && (
                <FormErrorMessage>{errors.description.message}</FormErrorMessage>
              )}
            </FormControl>
            <Flex mt={4} gap={3}>
              <Button
                variant="primary"
                onClick={toggleEditMode}
                type={editMode ? "button" : "submit"}
                isLoading={editMode ? isSubmitting : false}
                // isDisabled={editMode ? !isDirty || !getValues("description") : false}
              >
                {editMode ? "Save" : "Edit"}
              </Button>
              {editMode && (
                <Button onClick={onCancel} isDisabled={isSubmitting}>
                  Cancel
                </Button>
              )}
            </Flex>
          </Box>
        </Container>
      </>
    )
  }
  
  export default BusinessCabinet
  