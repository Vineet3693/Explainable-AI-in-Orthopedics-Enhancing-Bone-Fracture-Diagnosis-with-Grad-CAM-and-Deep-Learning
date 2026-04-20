import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const ChatPage: React.FC = () => {
    return (
        <Container maxWidth="lg">
            <Typography variant="h4">Q&A Chat</Typography>
            <Box sx={{ mt: 2 }}>
                Chat interface will be here
            </Box>
        </Container>
    );
};

export default ChatPage;
