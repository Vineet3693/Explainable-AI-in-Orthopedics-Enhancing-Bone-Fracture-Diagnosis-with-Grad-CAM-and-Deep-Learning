import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const HistoryPage: React.FC = () => {
    return (
        <Container maxWidth="lg">
            <Typography variant="h4">Analysis History</Typography>
            <Box sx={{ mt: 2 }}>
                History will be displayed here
            </Box>
        </Container>
    );
};

export default HistoryPage;
