import {
    Button,
    FormControl,
    FormLabel,
    Input,
    InputGroup,
    Icon,
    WrapItem,
    Avatar,
    Box,
    Divider,
    Stack,
    Center,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient} from "@tanstack/react-query"
  import { FiUpload } from "react-icons/fi"
  import {
    type EmployeePublic,
    EmployeesService,
    AvatarUploadInput,
    type ApiError,
  } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { useState, useEffect } from "react"
import { type SubmitHandler, useForm, FormProvider } from "react-hook-form"
import { handleError } from "../../utils"




function EmployeeAvatarUpload(
    { employee }: { employee: EmployeePublic }) 
    {
    const showToast = useCustomToast()
    const queryClient = useQueryClient()
    const [avatar, setAvatar] = useState("http://localhost/api/v1/employee/get_avatar/"+employee?.avatar)
    const formMethods = useForm<AvatarUploadInput>({
      mode: "onBlur",
      criteriaMode: "all"
    })
    const {
      register,
      handleSubmit,
      reset,
      // getValues,
      formState: { isSubmitting, errors },
    } = formMethods

    function handleSelectImage(event: React.ChangeEvent<HTMLInputElement>) {
      const file = event.target.files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setAvatar(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      }
    }
    const mutation = useMutation({
      mutationFn: (data: AvatarUploadInput) =>
        EmployeesService.updateEmployeeAvatar({ avatarFile: data.avatarFile[0]! }),
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
  
    const onSubmit: SubmitHandler<AvatarUploadInput> = async (data) => {
      mutation.mutate(data)
    }
    useEffect(() => {      
      if (employee) {
        setAvatar("http://localhost/api/v1/employee/get_avatar/"+employee?.avatar)
        console.log("Employee updated", employee)
      } else {
        console.log("loading avatar", employee)
      }
    }
    , [employee])

    return (
      <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
          onSubmit={handleSubmit(onSubmit)}
        >
      <FormControl id="avatarFile" isInvalid>
        <Stack direction='row' h={{ sm: "full", md: "50%" }} w={{ sm: "full", md: "50%" }}>
          <Center height='130px'>
            <Divider orientation='vertical' />
          </Center>
          <FormLabel htmlFor="avatarFile" srOnly>
            Upload Avatar
          </FormLabel>
          <WrapItem>
            <Avatar size='2xl' name={employee?.name} src={avatar} loading="lazy"/>
          </WrapItem>
        <Stack>
        <InputGroup w='300px'>
          <Input
            type="file"
            id="avatarFile"
            {...register("avatarFile")}
            accept="image/*"
            display='md'
            multiple={false}
            onChange={handleSelectImage}
          />
        </InputGroup>
        <Stack direction='row' spacing={4}>
            <Button
              type="submit"
              isLoading={isSubmitting}
              leftIcon={<Icon as={FiUpload} />}
              mt={2}
            >
              Upload
            </Button>
        </Stack>
        </Stack>
        </Stack>
      </FormControl>
      </Box>
    )
  }
  export default EmployeeAvatarUpload