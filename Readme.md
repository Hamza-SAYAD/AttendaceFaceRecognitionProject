## Streamlit Attendance and Mask Detection App with Location Tracking

This Streamlit application provides a comprehensive solution for managing student attendance, real-time mask detection, and location tracking. It offers functionalities for:

* **Student Management:**
    * Add new students with details like name, major, starting year, and optional location data.
    * View and update existing student information, including location.
    * Delete students from the system (optional: with confirmation dialog).
* **Attendance Tracking:**
    * Start the attendance system, potentially using a camera or attendance code input.
    * Optionally, record student location (e.g., classroom, library) during attendance marking.
    * Visualize student attendance data in a table format, including location information (if available).
    * Include "Delete" buttons in the table for individual student record removal (optional: with confirmation dialog).
* **Mask Detection:**
    * Utilize a machine learning model for real-time mask detection.
    * Display a visual indication of mask detection status (e.g., masked/unmasked) and potentially location information (if applicable).
* **Data Visualization:**
    * Generate insightful graphs and charts to analyze attendance trends, incorporating location data (if available).
    * Visualize metrics like: total attendance by student, number of students by standing, attendance distribution by location (optional: using donut charts, line graphs, pie charts).

## Features

* **Sophisticated Theme:** Customize the application's visual style with a user-friendly color theme and font selection. 
* **Performance Optimization:** Enhance app responsiveness through features like hot reloading and script caching.
* **Error Handling:** Implement mechanisms to gracefully handle potential errors and provide informative feedback to users.
* **Responsive Design:** Ensure the application adapts seamlessly to different screen sizes for optimal user experience.
* **Location Tracking (Optional):** Integrate a method to capture student location during attendance marking or provide a way for students to report their location.

## Getting Started

1. **Prerequisites:**
    * Python 3.x
    * Streamlit: `pip install streamlit`
    * Additional libraries for attendance tracking, mask detection, and location tracking (specific libraries will depend on your chosen implementation)
2. **Clone the Repository:** (Replace `<repository_url>` with the actual URL)

   ```bash
   git clone <repository_url>
   ```

3. **Install Dependencies:** (Replace `requirements.txt` with your actual file name if different)

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App:**

   ```bash
   streamlit run main.py
   ```

## Configuration (.toml file - Optional)

A sample configuration file (`config.toml`) can be created to customize various aspects of the application, including:

* Theme colors and fonts
* Server settings (hot reloading, log level)
* Application settings (auto-generated titles, favicon, responsiveness)
* Data loading timeout (optional)



Config file :
	You  have to copy the config.toml file located in the project to the streamlit hided file (.streamlit ) located in the user directory of your machine

## Usage

The application provides a user-friendly interface with clear navigation options for managing students, tracking attendance with optional location recording, viewing mask detection results, and analyzing data through visualizations incorporating location information (if available). 

Location :
    You got to have a browser with your real actual position, in order to be able get authorised to use this app !!

**Note:** Specific instructions for adding students, tracking attendance with location data (if chosen), interacting with the mask detection features, and analyzing visualizations will depend on the implementation details of your chosen libraries and code structure. Refer to the application code and any additional documentation provided for detailed usage instructions.

## Further Customization

This application provides a solid foundation for managing attendance, mask detection, and location tracking with Streamlit. You can further customize it by:

* Integrating additional functionalities based on your specific needs.
* Implementing more advanced data analysis features that leverage location data.
* Creating custom visualizations tailored to your data insights and location information.

## Contributing

We welcome contributions to improve this application. Feel free to fork the repository and submit pull requests with your enhancements.
