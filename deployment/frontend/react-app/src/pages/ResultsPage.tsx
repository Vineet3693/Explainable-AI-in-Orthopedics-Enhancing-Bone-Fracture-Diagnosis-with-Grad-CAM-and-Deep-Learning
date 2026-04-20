import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const ResultsPage: React.FC = () => {
    return (
        <Container maxWidth="lg">
            <Typography variant="h4">Results Page</Typography>
            <Box sx={{ mt: 2 }}>
                Results will be displayed here
            </Box>
        </Container>
    );
};

export default ResultsPage;
