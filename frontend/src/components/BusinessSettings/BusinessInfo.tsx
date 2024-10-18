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
    useColorModeValue
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient } from "@tanstack/react-query"
  import { useState } from "react"
  import { type SubmitHandler, useForm } from "react-hook-form"
  
  import {
    type ApiError,
    type BusinessPublic,
    type BusinessUpdate,
    BusinessesService,
  } from "../../client"
  import useBusiness from "../../hooks/useBusiness"
  import useCustomToast from "../../hooks/useCustomToast"
  import { handleError } from "../../utils"
  
  const BusinessInfo = () => {
    const queryClient = useQueryClient()
    const color = useColorModeValue("inherit", "ui.light")
    const showToast = useCustomToast()
    const [editMode, setEditMode] = useState(false)
    const { business: currentBusiness } = useBusiness()
    const {
      register,
      handleSubmit,
      reset,
      // getValues,
      formState: { isSubmitting, errors },
    } = useForm<BusinessPublic>({
      mode: "onBlur",
      criteriaMode: "all",
      defaultValues: {
        name: currentBusiness?.name,
        organizational_type: currentBusiness?.organizational_type,
        national_id: currentBusiness?.national_id,
        national_id_type: currentBusiness?.national_id_type,
        address: currentBusiness?.address,
        phone: currentBusiness?.phone,
        email: currentBusiness?.email,
        website: currentBusiness?.website,
        bank_account: currentBusiness?.bank_account,
        logo: currentBusiness?.logo,
      },
    })
  
    const toggleEditMode = () => {
      setEditMode(!editMode)
    }
  
    const mutation = useMutation({
      mutationFn: (data: BusinessUpdate) =>
        BusinessesService.updateBusiness({ requestBody: data, id: currentBusiness!.id }),
      onSuccess: () => {
        showToast("Success!", "Business updated successfully.", "success")
      },
      onError: (err: ApiError) => {
        handleError(err, showToast)
      },
      onSettled: () => {
        queryClient.invalidateQueries()
      },
    })
  
    const onSubmit: SubmitHandler<BusinessUpdate> = async (data) => {
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
            Employee Information
          </Heading>
          <Box
            w={{ sm: "full", md: "50%" }}
            as="form"
            onSubmit={handleSubmit(onSubmit)}
          >
            <FormControl>
              <FormLabel color={color} htmlFor="name">
                Company name
              </FormLabel>
              {editMode ? (
                <Input
                  id="name"
                  {...register("name", { maxLength: 30 })}
                  type="text"
                  size="md"
                  w="auto"
                  defaultValue={currentBusiness?.name || "N/A"}
                />
              ) : (
                <Text
                  size="md"
                  py={2}
                  color={!currentBusiness?.name ? "ui.dim" : "inherit"}
                  isTruncated
                  maxWidth="250px"
                >
                  {currentBusiness?.name || "N/A"}
                </Text>
              )}
            </FormControl>
            <FormControl mt={4} isInvalid={!!errors.organizational_type}>
              <FormLabel color={color} htmlFor="organizational_type">
                Organizational type
              </FormLabel>
              {editMode ? (
                <Input
                  id="organizational_type"
                  {...register("organizational_type", { maxLength: 30 })}
                  type="text"
                  size="md"
                  w="auto"
                  defaultValue={currentBusiness?.organizational_type || "N/A"}
                />
              ) : (
                <Text size="md" py={2} isTruncated maxWidth="250px">
                  {currentBusiness?.organizational_type || "N/A"}
                </Text>
              )}
              {errors.organizational_type && (
                <FormErrorMessage>{errors.organizational_type.message}</FormErrorMessage>
              )}
            </FormControl>
            <Flex mt={4} gap={3}>
              <Button
                variant="primary"
                onClick={toggleEditMode}
                type={editMode ? "button" : "submit"}
                isLoading={editMode ? isSubmitting : false}
                // isDisabled={editMode ? !isDirty || !getValues("organizational_type") : false}
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
          <Box>
            <Text mt={4} fontSize="sm" color="ui.dim">
              * This information is visible to all employees in your company.
            </Text>
          </Box>
        </Container>
      </>
    )
  }
  
  export default BusinessInfo
  