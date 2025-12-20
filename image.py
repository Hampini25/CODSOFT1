import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.File;

public class ImageCaptioningAI extends JFrame {

    JLabel imageLabel;
    JLabel captionLabel;
    JButton uploadButton, captionButton;
    File selectedImage;

    public ImageCaptioningAI() {
        setTitle("Image Captioning AI");
        setSize(600, 500);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Image display
        imageLabel = new JLabel("No Image Selected", JLabel.CENTER);
        imageLabel.setPreferredSize(new Dimension(400, 300));
        add(imageLabel, BorderLayout.CENTER);

        // Caption label
        captionLabel = new JLabel("Caption will appear here", JLabel.CENTER);
        captionLabel.setFont(new Font("Arial", Font.BOLD, 14));
        add(captionLabel, BorderLayout.SOUTH);

        // Buttons panel
        JPanel panel = new JPanel();
        uploadButton = new JButton("Upload Image");
        captionButton = new JButton("Generate Caption");

        panel.add(uploadButton);
        panel.add(captionButton);
        add(panel, BorderLayout.NORTH);

        // Upload button action
        uploadButton.addActionListener(e -> uploadImage());

        // Caption button action
        captionButton.addActionListener(e -> generateCaption());

        setVisible(true);
    }

    // Upload image
    void uploadImage() {
        JFileChooser chooser = new JFileChooser();
        int result = chooser.showOpenDialog(this);

        if (result == JFileChooser.APPROVE_OPTION) {
            selectedImage = chooser.getSelectedFile();
            ImageIcon icon = new ImageIcon(
                    new ImageIcon(selectedImage.getAbsolutePath())
                            .getImage()
                            .getScaledInstance(350, 250, Image.SCALE_SMOOTH)
            );
            imageLabel.setIcon(icon);
            imageLabel.setText("");
            captionLabel.setText("Image loaded. Click Generate Caption.");
        }
    }

    // Simulated Image Captioning
    void generateCaption() {
        if (selectedImage == null) {
            JOptionPane.showMessageDialog(this, "Please upload an image first!");
            return;
        }

        // ---- Simulated CNN + NLP ----
        String imageName = selectedImage.getName().toLowerCase();
        String caption;

        if (imageName.contains("dog")) {
            caption = "A dog is sitting calmly on the ground.";
        } else if (imageName.contains("cat")) {
            caption = "A cat is relaxing indoors.";
        } else if (imageName.contains("car")) {
            caption = "A car is parked on the roadside.";
        } else if (imageName.contains("person")) {
            caption = "A person is standing and posing for the photo.";
        } else {
            caption = "An object is present in the image.";
        }

        captionLabel.setText("Caption: " + caption);
    }

    public static void main(String[] args) {
        new ImageCaptioningAI();
    }
}