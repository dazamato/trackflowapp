import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    ModalCloseButton,
    Button,
    useDisclosure,
    useColorModeValue,
    Container,
    FormControl,
    Input,
    FormErrorMessage,
    InputGroup,
    InputRightElement,
    Icon,
    Image,
    Heading,
  } from '@chakra-ui/react'
import Logo from "/assets/images/trackflow-logo.svg"
import { emailPattern } from "../../utils"
import { useMutation, useQueryClient} from "@tanstack/react-query"
import { FiUpload } from "react-icons/fi"
import {
type EmployeePublic,
type InviteRequest,
EmployeesService,
AvatarUploadInput,
type ApiError,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { useState, useEffect } from "react"
import { type SubmitHandler, useForm, FormProvider } from "react-hook-form"
import { handleError } from "../../utils"
import useEmployee from '../../hooks/useEmployee'
import useBusiness from '../../hooks/useBusiness'

const AddEmployeeToBusiness = () =>{
    const { isOpen, onOpen, onClose } = useDisclosure()
    const queryClient = useQueryClient()
    const showToast = useCustomToast()
    const [editMode, setEditMode] = useState(false)
    const { employee: currentEmployee } = useEmployee()
    const { business: currentBusiness } = useBusiness()
    const formMethods = useForm<InviteRequest>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            email: "",
            business_id: currentEmployee!.business_id,
        },
    })
    const {
        register,
        handleSubmit,
        reset,
        // getValues,
        formState: { isSubmitting, errors },
    } = formMethods

    const mutation = useMutation({
        mutationFn: (data: InviteRequest) =>
        EmployeesService.inviteEmployee(data=data),
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

    const onSubmit: SubmitHandler<InviteRequest> = async (data) => {
        console.log(currentEmployee)
        data.business_id = currentBusiness!.id
        mutation.mutate(data)
    }

    const onCancel = () => {
        reset()
        onClose()
    }
    return (
        <Container maxW="full">
        <Heading size="sm" py={4}>
          Current Employee list of your business
        </Heading>
        <p>
            Here you can add new employee to your business, by sending him an invitation using his email. 
        </p>
        <p>
            Just press the button below and fill the email of new employee.
        </p>
        <p>He will receive an email with invitation link.</p>
        <p>After he accepts the invitation, he will be able to join your business.</p>
        <p>He will be able to see the data of your business, according to his role permissions.</p>
        <Button onClick={onOpen}>Invite new employee</Button>

        <Modal isOpen={isOpen} onClose={onCancel}>
            <ModalOverlay />
            <ModalContent>
            <ModalHeader>Sending Invitation</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
                <Container
                    as="form"
                    onSubmit={handleSubmit(onSubmit)}
                    h="30vh"
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
                    <FormControl id="email" isInvalid={!!errors.email }>
                    <Input
                        id="email"
                        {...register("email", {
                        required: "Email to send ivitation is required",
                        pattern: emailPattern,
                        })}
                        placeholder="Email"
                        type="email"
                        required
                    />
                    {errors.email && (
                        <FormErrorMessage>{errors.email.message}</FormErrorMessage>
                    )}
                    </FormControl>
                    <Button variant="primary" type="submit" isLoading={isSubmitting}>
                    Send
                    </Button>
                </Container>
            </ModalBody>
            </ModalContent>
        </Modal>
        </Container>
    )
    }
export default AddEmployeeToBusiness