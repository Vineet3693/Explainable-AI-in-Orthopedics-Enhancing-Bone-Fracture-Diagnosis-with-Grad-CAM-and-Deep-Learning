import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const SettingsPage: React.FC = () => {
    return (
        <Container maxWidth="lg">
            <Typography variant="h4">Settings</Typography>
            <Box sx={{ mt: 2 }}>
                Settings will be here
            </Box>
        </Container>
    );
};

export default SettingsPage;
