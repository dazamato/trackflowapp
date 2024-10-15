import {
    Container,
    Heading,
    Tab,
    TabList,
    TabPanel,
    TabPanels,
    Tabs,
  } from "@chakra-ui/react"
  import { useQueryClient } from "@tanstack/react-query"
  import { createFileRoute } from "@tanstack/react-router"
  
  import type { UserPublic, BusinessPublic } from "../../client"
//   import Appearance from "../../components/BusinessSettings/Appearance"
//   import ChangePassword from "../../components/BusinessSettings/ChangePassword"
//   import DeleteAccount from "../../components/BusinessSettings/DeleteAccount"
  import BusinessEmployeeInfo from "../../components/BusinessSettings/BusinessEmployeeInfo"
  import BusinessInfo from "../../components/BusinessSettings/BusinessInfo"
  
  const tabsConfig = [
    { title: "My Position", component: BusinessEmployeeInfo },
    { title: "Company information", component: BusinessInfo },
    // { title: "Appearance", component: Appearance },
    // { title: "Danger zone", component: DeleteAccount },
  ]
  
  export const Route = createFileRoute("/_layout/business-settings")({
    component: BusinessSettings,
  })
  
  function BusinessSettings() {
    const queryClient = useQueryClient()
    const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
    const currentBusiness = queryClient.getQueryData<BusinessPublic>(["currentBusiness"])
    const finalTabs = currentUser?.is_superuser
      ? tabsConfig.slice(0, 3)
      : tabsConfig
  
    return (
      <Container maxW="full">
        <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
          {currentBusiness?.name} Company Settings
        </Heading>
        <Tabs variant="enclosed">
          <TabList>
            {finalTabs.map((tab, index) => (
              <Tab key={index}>{tab.title}</Tab>
            ))}
          </TabList>
          <TabPanels>
            {finalTabs.map((tab, index) => (
              <TabPanel key={index}>
                <tab.component />
              </TabPanel>
            ))}
          </TabPanels>
        </Tabs>
      </Container>
    )
  }
  