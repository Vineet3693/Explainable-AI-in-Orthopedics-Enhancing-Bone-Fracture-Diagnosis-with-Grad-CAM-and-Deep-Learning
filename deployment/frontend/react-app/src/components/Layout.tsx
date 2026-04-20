import React, { useState } from 'react';
import {
    Box,
    AppBar,
    Toolbar,
    Typography,
    IconButton,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Avatar,
    useTheme,
    alpha,
} from '@mui/material';
import {
    Menu as MenuIcon,
    Home,
    CloudUpload,
    History,
    Chat,
    Settings,
    LocalHospital,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '@store/store';
import { toggleSidebar } from '@store/slices/uiSlice';

const drawerWidth = 280;

const menuItems = [
    { text: 'Home', icon: <Home />, path: '/' },
    { text: 'Upload X-Ray', icon: <CloudUpload />, path: '/upload' },
    { text: 'History', icon: <History />, path: '/history' },
    { text: 'Q&A Chat', icon: <Chat />, path: '/chat' },
    { text: 'Settings', icon: <Settings />, path: '/settings' },
];

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const dispatch = useAppDispatch();
    const sidebarOpen = useAppSelector((state) => state.ui.sidebarOpen);

    const handleDrawerToggle = () => {
        dispatch(toggleSidebar());
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* AppBar with vibrant gradient */}
            <AppBar
                position="fixed"
                sx={{
                    zIndex: theme.zIndex.drawer + 1,
                    background: 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)',
                    boxShadow: '0 4px 20px rgba(0, 212, 255, 0.3)',
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{ mr: 2 }}
                    >
                        <MenuIcon />
                    </IconButton>

                    <LocalHospital sx={{ mr: 2, fontSize: 32 }} />

                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{
                            flexGrow: 1,
                            fontWeight: 700,
                            fontSize: '1.5rem',
                            letterSpacing: '0.5px',
                        }}
                    >
                        Fracture Detection AI
                    </Typography>

                    <Avatar
                        sx={{
                            background: 'linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)',
                            fontWeight: 600,
                        }}
                    >
                        DR
                    </Avatar>
                </Toolbar>
            </AppBar>

            {/* Sidebar with glass morphism */}
            <Drawer
                variant="persistent"
                open={sidebarOpen}
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    '& .MuiDrawer-paper': {
                        width: drawerWidth,
                        boxSizing: 'border-box',
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(20px)',
                        borderRight: '1px solid rgba(0, 212, 255, 0.1)',
                        boxShadow: '4px 0 24px rgba(0, 0, 0, 0.05)',
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: 'auto', mt: 2, px: 2 }}>
                    <List>
                        {menuItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            return (
                                <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
                                    <ListItemButton
                                        onClick={() => navigate(item.path)}
                                        sx={{
                                            borderRadius: 3,
                                            py: 1.5,
                                            background: isActive
                                                ? 'linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)'
                                                : 'transparent',
                                            color: isActive ? '#FFFFFF' : theme.palette.text.primary,
                                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                            '&:hover': {
                                                background: isActive
                                                    ? 'linear-gradient(135deg, #00A3CC 0%, #5E35B1 100%)'
                                                    : alpha(theme.palette.primary.main, 0.08),
                                                transform: 'translateX(8px)',
                                            },
                                        }}
                                    >
                                        <ListItemIcon
                                            sx={{
                                                color: isActive ? '#FFFFFF' : theme.palette.primary.main,
                                                minWidth: 40,
                                            }}
                                        >
                                            {item.icon}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={item.text}
                                            primaryTypographyProps={{
                                                fontWeight: isActive ? 600 : 500,
                                            }}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>
            </Drawer>

            {/* Main content */}
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3,
                    width: { sm: `calc(100% - ${sidebarOpen ? drawerWidth : 0}px)` },
                    ml: { sm: sidebarOpen ? 0 : `-${drawerWidth}px` },
                    transition: theme.transitions.create(['margin', 'width'], {
                        easing: theme.transitions.easing.sharp,
                        duration: theme.transitions.duration.leavingScreen,
                    }),
                }}
            >
                <Toolbar />
                {children}
            </Box>
        </Box>
    );
};

export default Layout;
