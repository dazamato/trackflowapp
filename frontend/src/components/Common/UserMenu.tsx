import {
  Box,
  IconButton,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  WrapItem,
  Avatar,
} from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { FaUserAstronaut } from "react-icons/fa"
import { FiLogOut, FiUser } from "react-icons/fi"

import useAuth from "../../hooks/useAuth"
import useEmployee from "../../hooks/useEmployee"

const UserMenu = () => {
  const { logout } = useAuth()
  const { employee } = useEmployee()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>
      {/* Desktop */}
      <Box
        display={{ base: "none", md: "block" }}
        position="fixed"
        top={4}
        right={4}
      >
        <Menu>
          {
            employee? (
              <MenuButton
              as={IconButton}
              aria-label="Options"
              bg="ui.main"
              isRound
              data-testid="user-menu"
            >
              <WrapItem>
                <Avatar name={employee.name} src={"http://localhost/api/v1/employee/get_avatar/"+employee.avatar} loading="lazy"/>
              </WrapItem>
              </MenuButton>
            ) : 
            (<MenuButton
              as={IconButton}
              aria-label="Options"
              icon={<FaUserAstronaut color="#DF7861" fontSize="18px" />}
              bg="ui.main"
              isRound
              data-testid="user-menu"
            />)

          }
          
          <MenuList>
            <MenuItem icon={<FiUser fontSize="18px" />} as={Link} to="settings">
              My profile
            </MenuItem>
            <MenuItem
              icon={<FiLogOut fontSize="18px" />}
              onClick={handleLogout}
              color="ui.danger"
              fontWeight="bold"
            >
              Log out
            </MenuItem>
          </MenuList>
        </Menu>
      </Box>
    </>
  )
}

export default UserMenu
